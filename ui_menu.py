#!/usr/bin/env python3
from . import shared
from .download import *
from .log import *

import time

from aqt import mw
from aqt.qt import *
from aqt.utils import showWarning, showInfo

def network_dialog():
  dialog = QDialog(mw)
  dialog.setWindowTitle("Network Settings")

  warning = QLabel(shared.s_PROXY_WARN)

  sysproxy = QRadioButton("Use System Proxy")
  manproxy = QRadioButton("Manual HTTP/HTTPS Proxy")

  proxybox = QGroupBox("Proxy Settings")
  addressbox = QLineEdit()
  colon = QLabel(":")
  portbox = QLineEdit()
  portbox.setValidator(QIntValidator())
  test = QPushButton("Test Connection to Google")

  hackhttps = QCheckBox("Bypass HTTPS Verification")
  info = QLabel(shared.s_PROXY_HTTPS_VERIFY_BYPASS_INFO)
  info.setTextFormat(Qt.RichText)
  info.setTextInteractionFlags(Qt.TextBrowserInteraction)
  info.setOpenExternalLinks(True)

  ok = QDialogButtonBox(QDialogButtonBox.Ok)
  cancel = QDialogButtonBox(QDialogButtonBox.Cancel)

  def toggle_proxy_settings(b_checked):
    addressbox.setEnabled(b_checked)
    portbox.setEnabled(b_checked)
  manproxy.toggled.connect(toggle_proxy_settings)

  # Config, UI, conversions
  def init_configui():
    config = shared.config_netconfig
    sysproxy.setChecked(config["use_system_proxy"])
    manproxy.setChecked(not config["use_system_proxy"])
    addressbox.setText(config["proxy_addr"])
    portbox.setText(str(config["proxy_port"]))
    hackhttps.setChecked(config["assign_https_context"])
    toggle_proxy_settings(not config["use_system_proxy"])

  def read_config():
    return \
      { "use_system_proxy" : sysproxy.isChecked()
      , "proxy_addr" : addressbox.text()
      , "proxy_port" : int(portbox.text())
      , "assign_https_context" : hackhttps.isChecked()
      }

  def confirm_config():
    shared.config_netconfig = read_config()
    write_netconfig()
    dialog.close()

  def test_connection():
    config = read_config()
    config_bkp = shared.config_netconfig
    shared.config_netconfig = config
    start = time.time()
    mw.progress.start(immediate=True)
    (_, so_error) = fetch_page("https://www.google.com")
    mw.progress.finish()
    if so_error:
      showWarning("Connection failed with %s" % so_error)
    else:
      end = time.time()
      showInfo("Connection is good, took %s seconds" % (end - start))
    shared.config_netconfig = config_bkp

  def layout_everything():
    layout = QVBoxLayout()
    dialog.setLayout(layout)

    layout.addWidget(warning)

    layout.addWidget(sysproxy)
    layout.addWidget(manproxy)
    layout.addWidget(proxybox)

    proxyboxlayout = QHBoxLayout()
    proxybox.setLayout(proxyboxlayout)
    proxyboxlayout.addWidget(addressbox)
    proxyboxlayout.addWidget(colon)
    proxyboxlayout.addWidget(portbox)

    layout.addWidget(hackhttps)
    layout.addWidget(info)

    layout.addWidget(test)

    layout.addWidget(ok)
    layout.addWidget(cancel)

  init_configui()
  ok.clicked.connect(confirm_config)
  cancel.clicked.connect(dialog.close)
  test.clicked.connect(test_connection)

  layout_everything()

  dialog.exec_()

# unit -> unit
def buildMenu():
  menu = QMenu(mw)
  menu.setTitle("Image Search")
  mw.form.menuTools.addAction(menu.menuAction())

  # (string, string option, unit -> unit) list
  l_t_ssofuu_MENU_ITEMS = \
    [ ("Network Config", None, network_dialog)
    ]

  for elem in l_t_ssofuu_MENU_ITEMS:
    (s_title, so_shortcut, func) = elem
    action = QAction(menu)
    action.setText(s_title)
    if so_shortcut:
      action.setShortcut(so_shortcut)
    menu.addAction(action)
    action.triggered.connect(func)

buildMenu()

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def patch_file(path, replacements):
    if not os.path.exists(path):
        print(f"[!] File not found: {path}")
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"[+] Patched {path}")
        else:
            print(f"[?] Pattern skipped in {path}: {old[:35]}...")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# 1. FemGram Branding + TGWS Proxy Auto-launcher & Process Manager
app_cpp = "Telegram/SourceFiles/core/application.cpp"
patch_file(app_cpp, [
    (
        '#include "core/application.h"',
        '''#include "core/application.h"
#include "ayu/ayu_settings.h"
#include <QtCore/QProcess>
#include <QtCore/QCoreApplication>
#include <QtCore/QFileInfo>

static QProcess *g_tgwsProcess = nullptr;

void UpdateTgWsProxyState(bool enabled) {
    const auto proxyExe = QCoreApplication::applicationDirPath() + "/modules/TgWsProxy_windows.exe";
    if (enabled) {
        if (QFileInfo::exists(proxyExe) && !g_tgwsProcess) {
            g_tgwsProcess = new QProcess();
            g_tgwsProcess->setProgram(proxyExe);
            g_tgwsProcess->setArguments({"--port", "1443", "--secret", "0123456789abcdef0123456789abcdef"});
            g_tgwsProcess->start();
        }
    } else if (g_tgwsProcess) {
        g_tgwsProcess->kill();
        g_tgwsProcess->waitForFinished(1000);
        delete g_tgwsProcess;
        g_tgwsProcess = nullptr;
    }
}'''
    ),
    (
        'void Application::run() {',
        '''void Application::run() {
    UpdateTgWsProxyState(AyuSettings::getInstance().useTgWsProxy);'''
    ),
    (
        'Application::~Application() {',
        '''Application::~Application() {
    UpdateTgWsProxyState(false);'''
    )
])

# 2. Settings fields in AyuSettings (TGWS Toggle + Context Menu Order)
ayu_settings_h = "Telegram/SourceFiles/ayu/ayu_settings.h"
patch_file(ayu_settings_h, [
    (
        "int wideMultiplier = 1;",
        '''int wideMultiplier = 1;
    bool useTgWsProxy = true;
    std::string contextMenuOrder = "forward,translate,reply,copy,pin,delete";'''
    )
])

ayu_settings_cpp = "Telegram/SourceFiles/ayu/ayu_settings.cpp"
patch_file(ayu_settings_cpp, [
    (
        'j["wideMultiplier"] = wideMultiplier;',
        '''j["wideMultiplier"] = wideMultiplier;
    j["useTgWsProxy"] = useTgWsProxy;
    j["contextMenuOrder"] = contextMenuOrder;'''
    ),
    (
        'wideMultiplier = j.value("wideMultiplier", 1);',
        '''wideMultiplier = j.value("wideMultiplier", 1);
    useTgWsProxy = j.value("useTgWsProxy", true);
    contextMenuOrder = j.value("contextMenuOrder", std::string("forward,translate,reply,copy,pin,delete"));'''
    )
])

# 3. Femboy Aesthetic Palette (Pastel Pink & Lavender Default Theme)
theme_path = "Telegram/Resources/colors.palette"
patch_file(theme_path, [
    ("windowBg: #ffffff;", "windowBg: #fff0f6;"),
    ("windowBgOver: #f1f1f1;", "windowBgOver: #ffdeeb;"),
    ("windowBgRipple: #e5e5e5;", "windowBgRipple: #fcc2d7;"),
    ("windowBgActive: #40a7e3;", "windowBgActive: #f06595;"),
    ("activeButtonBg: #40a7e3;", "activeButtonBg: #f06595;"),
    ("activeButtonBgOver: #399ad4;", "activeButtonBgOver: #e64980;"),
    ("activeButtonBgRipple: #328ec4;", "activeButtonBgRipple: #d6336c;"),
    ("msgOutBg: #effdde;", "msgOutBg: #ffdeeb;"),
    ("msgOutBgSelected: #d4f1ba;", "msgOutBgSelected: #fcc2d7;"),
    ("msgInBg: #ffffff;", "msgInBg: #f8f0fc;"),
    ("msgInBgSelected: #e8f3fa;", "msgInBgSelected: #f3d9fa;"),
    ("historyPeer1NameFg: #c03d33;", "historyPeer1NameFg: #d6336c;"),
    ("historyPeer2NameFg: #4fad2d;", "historyPeer2NameFg: #ae3ec9;"),
    ("historyPeer4NameFg: #168acd;", "historyPeer4NameFg: #f06595;")
])

print("[*] FemGram patching completed successfully!")

import wx
from wget import download
from settings import *
from filehandle import *
import wx.adv


dlcs = Dlcload()


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            None,
            title="简易接档器",
            size=(500, 300),
            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX,
        )
        self.SetSizeHints(500, 300, 500, 300)
        self.SetMaxSize((500, 300))
        icon = wx.Icon(get_resource_path("fengmian.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.panel = wx.Panel(self)
        hintText = wx.StaticText(
            self.panel,
            label="提示:请先将要接的档放在与本程序\n同目录下，不用解压",
            pos=(50, 20),
        )
        font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        hintText.SetFont(font)
        hintText.SetForegroundColour(wx.Colour(102, 209, 255))
        loadButton = wx.Button(self.panel, label="安装", pos=(60, 70))
        loadButton.Bind(wx.EVT_BUTTON, self.onLoadButtonClicked)
        unloadButton = wx.Button(self.panel, label="卸载", pos=(150, 70))
        unloadButton.Bind(wx.EVT_BUTTON, self.onUnloadButtonClicked)
        cleanButton = wx.Button(self.panel, label="清理", pos=(240, 70))
        cleanButton.Bind(wx.EVT_BUTTON, self.onCleanButtonClicked)
        authorText = wx.StaticText(
            self.panel, label="作者：wenwen12\n我是神里绫华的狗", pos=(380, 220)
        )
        authorText.SetForegroundColour(wx.Colour(102, 209, 255))
        self.gamedirText = wx.TextCtrl(self.panel, pos=(50, 130), size=(300, -1))
        self.gamedirText.SetHint("游戏目录")
        GameDirChooserButton = wx.Button(
            self.panel, label="选择游戏目录", pos=(350, 130)
        )
        GameDirChooserButton.Bind(wx.EVT_BUTTON, self.onGameDirChooserButtonClicked)
        self.savingdirText = wx.TextCtrl(self.panel, pos=(50, 160), size=(300, -1))
        self.savingdirText.SetHint("存档目录")
        SavingDirChooserButton = wx.Button(
            self.panel, label="选择存档目录", pos=(350, 160)
        )
        SavingDirChooserButton.Bind(wx.EVT_BUTTON, self.onSavingDirChooserButtonClicked)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.ShowSetting()

    def onLoadButtonClicked(self, event):
        DOCUMENTS_DIR = self.savingdirText.GetValue()
        GAME_DIR = self.gamedirText.GetValue()
        File = findZipfile()
        if os.path.exists(GAME_DIR + "changed.json"):
            wx.MessageBox(
                "请先卸载再安装\n如果卸载没用，请尝试清理"
                "请先卸载",
                wx.OK | wx.ICON_ERROR,
            )
        elif File == None:
            wx.MessageBox(
                "您确定您把存档放在正确的位置了吗\n你应该放在" + os.getcwd(),
                "文件不存在",
                wx.OK | wx.ICON_ERROR,
            )
        else:
            processBar = wx.Gauge(self.panel)
            processBar.SetPosition((50, 100))
            processContent = wx.StaticText(self.panel)
            processContent.SetPosition((50, 120))
            processBar.SetValue(20)
            processContent.SetLabel("正在解压")
            configfile = getConfigFile(DOCUMENTS_DIR)
            with ZipFile(os.path.abspath(".") + "\\" + File, "r") as zip_ref:
                zip_ref.extractall(DOCUMENTS_DIR)
            processBar.SetValue(40)
            processContent.SetLabel("正在隐藏dlc")
            sig = {"savingPosition": get_recently_modified_folder(DOCUMENTS_DIR)}
            changedDLC = []
            for dlc in dlcs:
                if os.path.exists(GAME_DIR + dlc):
                    os.rename(GAME_DIR + dlc, GAME_DIR + dlc + ".disabled")
                    changedDLC.append(GAME_DIR + dlc + ".disabled")
            sig.update(changedDLC=changedDLC)
            with open(GAME_DIR + "changed.json", "w") as cre:
                dump(sig, cre)
            processBar.SetValue(60)
            processContent.SetLabel("正在更新游戏配置")
            if configfile:
                changeConfigFile(sig["savingPosition"], configfile)
            processBar.SetValue(80)
            processContent.SetLabel("正在删除缓存")
            os.remove(os.path.abspath(".") + "\\" + File)
            processBar.SetValue(100)
            processContent.SetLabel("安装完成")

    def onUnloadButtonClicked(self, event):
        GAME_DIR = self.gamedirText.GetValue()
        if os.path.exists(GAME_DIR + "changed.json"):
            with open(GAME_DIR + "changed.json") as sigFile:
                sig = load(sigFile)
            if os.path.exists(sig["savingPosition"]):
                rmtree(sig["savingPosition"])
            for DLC in sig["changedDLC"]:
                os.rename(DLC, DLC[:-8])
            os.remove(GAME_DIR + "changed.json")
            wx.MessageBox("已完成卸载", "卸载成功", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox(
                "发生错误，未找到卸载指示文件\n可能是因为你没有安装就卸载\n请检查游戏目录下是否存在changed.json\n若实在无法解决，请删除游戏文件夹中所有.disabled的文件，并检查完整性",
                "未找到文件",
                wx.OK | wx.ICON_ERROR,
            )

    def onCleanButtonClicked(self, event):
        GAME_DIR = self.gamedirText.GetValue()
        dlg = wx.MessageDialog(
            None,
            "执行清理操作后，将删除本程序对游戏的全部更改\n请注意，在清理完成后，您可能需要检查完整性才能继续使用",
            "清理提示",
            wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE,
        )
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            dlg = wx.MessageDialog(
                None,
                "这是最后一次提示，您确定要清理吗?",
                "清理提示",
                wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE,
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                delDisabled(GAME_DIR)
                if os.path.exists(GAME_DIR + "changed.json"):
                    os.remove(GAME_DIR + "changed.json")
                wx.MessageBox("清理完成", "清理完成", wx.OK | wx.ICON_INFORMATION)

    def onSavingDirChooserButtonClicked(self, event):
        dialog = wx.DirDialog(
            self.panel,
            "选择游戏存档文件夹，通常位置是 文档/euro truck simulator2/profiles",
            "",
            wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        if dialog.ShowModal() == wx.ID_OK:
            folder_path = (
                dialog.GetPath()
                if str(dialog.GetPath()).endswith("\\")
                else dialog.GetPath() + "\\"
            )
            if not folder_path.endswith(
                "Documents\\Euro Truck Simulator 2\\profiles\\"
            ):
                wx.MessageBox(
                    "目录选择错误，请注意查看选择器上方的提示\n位置是 文档/euro truck simulator2/profiles",
                    "目录选择错误",
                    wx.OK | wx.ICON_ERROR,
                )
                self.onSavingDirChooserButtonClicked(event)
            else:
                self.savingdirText.SetValue(folder_path)
        dialog.Destroy()

    def onGameDirChooserButtonClicked(self, event):
        dialog = wx.DirDialog(
            self.panel,
            "选择游戏路径文件夹，通常位置是Steam/steamapps/common/Euro Truck Simulator 2",
            "",
            wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        if dialog.ShowModal() == wx.ID_OK:
            folder_path = (
                dialog.GetPath()
                if str(dialog.GetPath()).endswith("\\")
                else dialog.GetPath() + "\\"
            )
            if not folder_path.endswith("\\common\\Euro Truck Simulator 2\\"):
                wx.MessageBox(
                    "目录选择错误，请注意查看选择器上方的提示\n位置是Steam/steamapps/common/Euro Truck Simulator 2",
                    "目录选择错误",
                    wx.OK | wx.ICON_ERROR,
                )
                self.onGameDirChooserButtonClicked(event)
            else:
                self.gamedirText.SetValue(folder_path)
            dialog.Destroy()

    def ShowSetting(self):
        setting = settingLoad()
        if isinstance(setting, Exception):
            wx.MessageBox(
                f"设置读取错误，详细信息:{setting}", "错误", wx.OK | wx.ICON_ERROR
            )
            setting = defaultJson
        self.savingdirText.SetValue(setting["gameDirectory"]["saving"])
        self.gamedirText.SetValue(setting["gameDirectory"]["game"])

    def TextLoad(self):
        return {
            "gameDirectory": {
                "saving": self.savingdirText.GetValue(),
                "game": self.gamedirText.GetValue(),
            },
        }

    def onClose(self, event):
        settingSave(self.TextLoad())
        self.Destroy()


if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()

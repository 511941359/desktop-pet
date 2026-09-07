# 🚀 GitHub Actions 在线打包指南

## 方法一：Fork 后自动打包（推荐）

### 1. 创建 GitHub 仓库
- 登录 [github.com](https://github.com)
- 新建一个仓库，比如 `my-desktop-pet`
- **不要** 初始化 README（我们已经准备好了）

### 2. 上传文件
把以下文件上传到仓库根目录：
```
desktop_pet.py
pet_char.png
requirements.txt
build.bat
README.md
DesktopPet.spec
.github/workflows/build.yml
.github/workflows/manual-build.yml
```

> 可以直接拖拽上传，或者用 Git 命令：
> ```bash
> git init
> git add .
> git commit -m "init"
> git remote add origin https://github.com/你的用户名/my-desktop-pet.git
> git push -u origin main
> ```

### 3. 自动触发打包
- 推送代码后，GitHub 会自动在 **Windows 服务器** 上运行打包
- 进入仓库 → Actions 标签页，可以看到打包进度
- 约 2-3 分钟后完成

### 4. 下载 EXE
- 打包完成后，进入 Actions 页面
- 点击最新的工作流运行记录
- 在 Artifacts 区域下载 `DesktopPet-Windows`
- 解压后得到 `DesktopPet.exe` 和 `pet_char.png`
- 放在同一文件夹，双击即可运行！

---

## 方法二：手动触发打包

如果你不想推送代码，只想打包当前版本：

1. 上传文件到仓库（同上）
2. 进入仓库 → Actions → **Manual Build EXE**
3. 点击右侧的 **Run workflow** 按钮
4. 等待 2-3 分钟
5. 下载 Artifacts 中的文件

---

## 方法三：发布 Release（带版本号）

如果你想生成带版本号的正式 release：

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions 会自动打包并发布到 Release 页面，可以直接下载。

---

## ⚡ 优势

- ✅ **完全免费**：GitHub Actions 对公开仓库免费
- ✅ **真正的 Windows 环境**：在微软官方的 Windows Server 上打包
- ✅ **无需安装任何软件**：不用装 Python、不用装 PyInstaller
- ✅ **随时随地**：手机、平板、Mac 上都能操作
- ✅ **自动发布**：可以自动上传到 Release，方便分享

---

## 📁 仓库文件结构示例

```
my-desktop-pet/
├── .github/
│   └── workflows/
│       ├── build.yml          # 自动打包（推送时触发）
│       └── manual-build.yml   # 手动打包
├── desktop_pet.py             # 主程序
├── pet_char.png               # 角色图片
├── requirements.txt           # 依赖
├── build.bat                  # 本地打包脚本
├── DesktopPet.spec            # 打包配置
└── README.md                  # 使用说明
```

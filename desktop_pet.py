
import sys
import random
import math
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QMenu, 
                              QAction, QInputDialog, QMessageBox, QWidget, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import (QPixmap, QCursor, QFont, QPainter, QColor, QPen, 
                         QBrush, QBitmap, QRegion, QImage)

class BubbleLabel(QLabel):
    """对话气泡 - 带小尾巴"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 230);
                color: #333;
                border: 2px solid #FF69B4;
                border-radius: 18px;
                padding: 10px 15px;
                font-size: 14px;
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
                font-weight: bold;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.hide()

    def show_text(self, text, duration=2500):
        self.setText(text)
        self.adjustSize()
        self.show()
        self.raise_()
        QTimer.singleShot(duration, self.hide)

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()

        # ========== 状态变量 ==========
        self.scale = 0.30
        self.base_size = (1179, 1572)
        self.is_dragging = False
        self.drag_pos = QPoint()
        self.is_topmost = True
        self.is_following = False
        self.is_walking = False
        self.is_sleeping = False
        self.anim_index = 0
        self.walk_dir = 1
        self.walk_step_count = 0
        self.drag_run_shown = False

        # 动画定时器引用
        self.anim_timer = None

        # ========== 对话池 ==========
        self.dialogues = {
            "jump": ["哇！飞起来啦~ ✨", "超级跳跃！🚀", "像小兔子一样蹦跶~ 🐰", "耶！好高呀！🎉"],
            "squash": ["哎呀！被压扁了~ 🍮", "好有弹性哦！🎈", "噗~回弹啦！💫", "像果冻一样Q弹！🍮"],
            "shake": ["摇摇晃晃~ 🌀", "头晕晕的~ 😵", "左右摇摆！💃", "嗨起来！🎵"],
            "drag": ["慢点慢点~ 💨", "要飞出去啦！✈️", "抓稳了哦！🎢", "冲冲冲！🏃‍♀️"],
            "chat": ["今天天气真好呢~ ☀️", "主人想我了吗？💕", "我在陪你哦~ 🤗", "要开心每一天！😊",
                    "有什么烦心事吗？🤔", "我会一直陪着你的~ ❤️", "要不要休息一下？☕", "你是最棒的！👍"],
            "pat": ["好舒服呀~ 😌", "摸摸头最喜欢了~ 🥰", "再摸一下嘛~ 👐", "嘿嘿，开心！😄"],
            "feed": ["好好吃！😋", "谢谢主人~ 🙏", "yummy！🍰", "吃饱饱才有力气~ 💪"],
            "walk": ["出发！🚶‍♀️", "一步一步走~ 👣", "散步时间到！🌸", "跟我来~ 👉"],
            "sleep": ["晚安~ 🌙", "呼呼... 💤", "做个好梦~ ⭐", "Zzz... 🛏️"],
            "follow": ["跟着主人走~ 🐾", "去哪里呀？🗺️", "我跟着你呢！👀", "别走太快哦~ 🏃"],
            "idle": ["好无聊呀~ 😔", "陪我玩嘛~ 🎮", "在发呆... 🤤", "主人~ 看看我~ 🥺", "我在这儿呢~ 👋"]
        }

        self.init_ui()
        self.init_timers()

    def init_ui(self):
        # 窗口：无边框、置顶、工具窗口（不在任务栏显示）
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 加载图片（支持同目录或打包后路径）
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        img_path = os.path.join(base_path, "pet_char.png")

        self.pixmap = QPixmap(img_path)
        if self.pixmap.isNull():
            QMessageBox.critical(None, "错误", f"找不到宠物图片！\n路径: {img_path}\n请确保 pet_char.png 与程序在同一目录。")
            sys.exit(1)

        # 提取alpha通道用于创建窗口遮罩
        self.alpha_mask = self.pixmap.createMaskFromColor(QColor(0,0,0,0), Qt.MaskInColor)

        # 主容器
        self.central = QWidget(self)
        self.setCentralWidget(self.central)

        # 角色显示标签
        self.pet_label = QLabel(self.central)
        self.pet_label.setScaledContents(True)
        self.update_pet_size()

        # 对话气泡
        self.bubble = BubbleLabel(self.central)

        # 设置窗口大小并居中显示
        self.update_window_geometry()
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            screen.height() - self.height() - 50
        )

        # 启用鼠标跟踪
        self.setMouseTracking(True)
        self.central.setMouseTracking(True)
        self.pet_label.setMouseTracking(True)

        # 应用遮罩（透明区域点击穿透）
        self.update_window_mask()

    def update_pet_size(self):
        """更新角色尺寸"""
        w = int(self.base_size[0] * self.scale)
        h = int(self.base_size[1] * self.scale)
        self.pet_label.setFixedSize(w, h)
        scaled_pixmap = self.pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pet_label.setPixmap(scaled_pixmap)

    def update_window_geometry(self):
        """更新窗口大小和位置"""
        margin = 120  # 气泡空间
        pw = self.pet_label.width()
        ph = self.pet_label.height()
        self.setFixedSize(pw + margin * 2, ph + margin * 2)
        self.pet_label.move(margin, margin)

    def update_window_mask(self):
        """根据角色形状更新窗口点击遮罩，实现透明区域穿透"""
        if self.pet_label.pixmap():
            # 获取缩放后的遮罩
            mask = self.alpha_mask.scaled(self.pet_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # 创建区域遮罩，偏移到角色在窗口中的位置
            region = QRegion(QBitmap(mask))
            region.translate(self.pet_label.x(), self.pet_label.y())
            self.setMask(region)

    def init_timers(self):
        # 跟随鼠标定时器
        self.follow_timer = QTimer(self)
        self.follow_timer.timeout.connect(self.follow_mouse_step)

        # 走路定时器
        self.walk_timer = QTimer(self)
        self.walk_timer.timeout.connect(self.walk_step)

        # 睡觉呼吸动画
        self.sleep_timer = QTimer(self)
        self.sleep_timer.timeout.connect(self.sleep_breath)
        self.sleep_phase = 0.0

        # 空闲随机气泡
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.on_idle)
        self.idle_timer.start(12000)  # 12秒

        # 走路时的随机气泡
        self.walk_chat_timer = QTimer(self)
        self.walk_chat_timer.timeout.connect(self.walk_chat)

    # ========== 气泡系统 ==========
    def show_bubble(self, category, duration=2500):
        if category not in self.dialogues:
            return
        text = random.choice(self.dialogues[category])
        self.bubble.setText(text)
        self.bubble.adjustSize()

        # 定位：角色上方居中
        px = self.pet_label.x()
        py = self.pet_label.y()
        bw = self.bubble.width()
        bx = px + (self.pet_label.width() - bw) // 2
        by = py - self.bubble.height() - 15

        # 边界保护
        if by < 5:
            by = py + self.pet_label.height() + 15  # 下方显示
        if bx < 5:
            bx = 5
        max_x = self.width() - bw - 5
        if bx > max_x:
            bx = max_x

        self.bubble.move(bx, by)
        self.bubble.show_text(text, duration)

    # ========== 互动动画 ==========
    def trigger_interaction(self):
        """点击角色轮流触发三种动画"""
        if self.is_sleeping:
            self.show_bubble("idle", 2000)
            return
        if self.is_dragging:
            return

        anims = [self.anim_jump, self.anim_squash, self.anim_shake]
        anims[self.anim_index % 3]()
        self.anim_index += 1

    def start_anim(self, callback):
        if self.anim_timer and self.anim_timer.isActive():
            self.anim_timer.stop()
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(callback)
        self.anim_timer.start(25)

    def anim_jump(self):
        self.show_bubble("jump")
        self.anim_frame = 0
        self.anim_orig_y = self.pet_label.y()
        self.start_anim(self._jump_frame)

    def _jump_frame(self):
        self.anim_frame += 1
        t = self.anim_frame / 24.0
        if t >= 1:
            self.pet_label.move(self.pet_label.x(), self.anim_orig_y)
            self.anim_timer.stop()
            return
        # 抛物线: 4 * h * t * (1-t)
        h = int(100 * self.scale)
        dy = int(-4 * h * t * (1 - t))
        self.pet_label.move(self.pet_label.x(), self.anim_orig_y + dy)

    def anim_squash(self):
        self.show_bubble("squash")
        self.anim_frame = 0
        self.start_anim(self._squash_frame)

    def _squash_frame(self):
        self.anim_frame += 1
        t = self.anim_frame / 20.0
        if t >= 1:
            self.update_pet_size()
            self.anim_timer.stop()
            return
        bw = self.base_size[0] * self.scale
        bh = self.base_size[1] * self.scale

        if t < 0.25:  # 压扁
            k = t / 0.25
            sx = 1 - 0.2 * k
            sy = 1 + 0.2 * k
        elif t < 0.5:  # 压到最扁
            sx, sy = 0.8, 1.2
        elif t < 0.75:  # 回弹拉长
            k = (t - 0.5) / 0.25
            sx = 0.8 + 0.3 * k
            sy = 1.2 - 0.3 * k
        else:  # 恢复
            k = (t - 0.75) / 0.25
            sx = 1.1 - 0.1 * k
            sy = 0.9 + 0.1 * k

        self.pet_label.setFixedSize(int(bw * sx), int(bh * sy))

    def anim_shake(self):
        self.show_bubble("shake")
        self.anim_frame = 0
        self.anim_orig_x = self.pet_label.x()
        self.start_anim(self._shake_frame)

    def _shake_frame(self):
        self.anim_frame += 1
        if self.anim_frame > 28:
            self.pet_label.move(self.anim_orig_x, self.pet_label.y())
            self.anim_timer.stop()
            return
        amp = int(18 * self.scale)
        dx = int(amp * math.sin(self.anim_frame * 0.9))
        self.pet_label.move(self.anim_orig_x + dx, self.pet_label.y())

    def on_idle(self):
        if not self.is_sleeping and not self.is_dragging and random.random() < 0.35:
            self.show_bubble("idle", 3000)

    # ========== 走路系统 ==========
    def start_walk(self):
        self.is_walking = True
        self.walk_timer.start(60)
        self.walk_chat_timer.start(4000)
        self.show_bubble("walk")

    def stop_walk(self):
        self.is_walking = False
        self.walk_timer.stop()
        self.walk_chat_timer.stop()
        self.update_pet_size()

    def walk_step(self):
        self.walk_step_count += 1
        screen = QApplication.primaryScreen().geometry()

        # 移动
        step = int(3 * self.walk_dir)
        new_x = self.x() + step
        if new_x < 0:
            new_x = 0
            self.walk_dir = 1
        elif new_x + self.width() > screen.width():
            new_x = screen.width() - self.width()
            self.walk_dir = -1
        self.move(new_x, self.y())

        # 走路起伏动画
        bounce = abs(math.sin(self.walk_step_count * 0.4)) * 0.08
        scale_y = 1 - bounce
        scale_x = 1 + bounce * 0.5
        w = int(self.base_size[0] * self.scale * scale_x)
        h = int(self.base_size[1] * self.scale * scale_y)
        self.pet_label.setFixedSize(w, h)

    def walk_chat(self):
        if random.random() < 0.4:
            self.show_bubble("walk", 2000)

    # ========== 睡觉系统 ==========
    def start_sleep(self):
        self.is_sleeping = True
        self.sleep_timer.start(1800)
        self.show_bubble("sleep", 5000)
        # 变暗效果
        self.pet_label.setStyleSheet("QLabel { opacity: 0.6; }")

    def stop_sleep(self):
        self.is_sleeping = False
        self.sleep_timer.stop()
        self.pet_label.setStyleSheet("")
        self.update_pet_size()

    def sleep_breath(self):
        self.sleep_phase += 0.15
        var = 0.03 * math.sin(self.sleep_phase)
        w = int(self.base_size[0] * self.scale * (1 + var))
        h = int(self.base_size[1] * self.scale * (1 - var))
        self.pet_label.setFixedSize(w, h)

    # ========== 跟随系统 ==========
    def start_follow(self):
        self.is_following = True
        self.follow_timer.start(40)
        self.show_bubble("follow")

    def stop_follow(self):
        self.is_following = False
        self.follow_timer.stop()

    def follow_mouse_step(self):
        cursor = QCursor.pos()
        target_x = cursor.x() - self.width() // 2
        target_y = cursor.y() - self.height() + int(self.pet_label.height() * 0.85)

        # 平滑跟随（缓动）
        cx, cy = self.x(), self.y()
        new_x = int(cx + (target_x - cx) * 0.12)
        new_y = int(cy + (target_y - cy) * 0.12)
        self.move(new_x, new_y)

    # ========== 鼠标事件 ==========
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 检查是否点在角色上（通过遮罩判断）
            local_pos = self.mapFromGlobal(event.globalPos())
            if self.mask().contains(local_pos):
                self.is_dragging = True
                self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            if not self.is_following:
                new_pos = event.globalPos() - self.drag_pos
                self.move(new_pos)

                # 拖动时随机显示跑姿对话
                if not self.drag_run_shown and random.random() < 0.015:
                    self.show_bubble("drag")
                    self.drag_run_shown = True
                    QTimer.singleShot(4000, lambda: setattr(self, 'drag_run_shown', False))
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.trigger_interaction()
            event.accept()

    def wheelEvent(self, event):
        """滚轮缩放"""
        delta = event.angleDelta().y()
        old_scale = self.scale
        if delta > 0:
            self.scale = min(self.scale + 0.03, 0.8)
        else:
            self.scale = max(self.scale - 0.03, 0.08)

        if self.scale != old_scale:
            # 以鼠标位置为中心缩放
            self.update_pet_size()
            self.update_window_geometry()
            self.update_window_mask()
        event.accept()

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(255, 255, 255, 245);
                border: 2px solid #FF69B4;
                border-radius: 12px;
                padding: 6px;
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 8px;
                color: #444;
            }
            QMenu::item:selected {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #FFB6C1, stop:1 #FF69B4);
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #E0E0E0;
                margin: 5px 12px;
            }
        """)

        def add_action(text, slot, checkable=False, checked=False):
            a = QAction(text, self)
            a.triggered.connect(slot)
            if checkable:
                a.setCheckable(True)
                a.setChecked(checked)
            menu.addAction(a)
            return a

        add_action("💬 陪我聊聊天", lambda: self.show_bubble("chat", 4000))
        add_action("👋 摸摸头", lambda: self.show_bubble("pat"))
        add_action("🍰 喂吃的", lambda: self.show_bubble("feed"))
        menu.addSeparator()

        add_action("🚶 让她走路" if not self.is_walking else "🛑 停止走路", self.toggle_walk)
        add_action("😴 让她睡觉" if not self.is_sleeping else "☀️ 唤醒她", self.toggle_sleep)
        add_action("🎯 跟随鼠标" if not self.is_following else "🚫 停止跟随", self.toggle_follow)
        menu.addSeparator()

        add_action("📏 调整大小...", self.size_dialog)
        add_action("📌 置顶: 开" if self.is_topmost else "📌 置顶: 关", self.toggle_topmost)
        menu.addSeparator()

        add_action("❌ 退出程序", self.close)

        menu.exec_(event.globalPos())

    def toggle_walk(self):
        if self.is_walking:
            self.stop_walk()
        else:
            self.stop_sleep()
            self.stop_follow()
            self.start_walk()

    def toggle_sleep(self):
        if self.is_sleeping:
            self.stop_sleep()
        else:
            self.stop_walk()
            self.stop_follow()
            self.start_sleep()

    def toggle_follow(self):
        if self.is_following:
            self.stop_follow()
        else:
            self.stop_walk()
            self.stop_sleep()
            self.start_follow()

    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.is_topmost:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self.update_window_mask()  # 重新应用遮罩

    def size_dialog(self):
        pct, ok = QInputDialog.getInt(self, "调整大小", "缩放百分比 (8-80):",
                                      int(self.scale * 100), 8, 80)
        if ok:
            self.scale = pct / 100.0
            self.update_pet_size()
            self.update_window_geometry()
            self.update_window_mask()

# ========== 启动入口 ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # 设置应用级字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())

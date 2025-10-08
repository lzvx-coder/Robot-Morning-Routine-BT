#!/usr/bin/env python3
"""
Robot's Morning Routine Behavior Tree
使用py_trees库实现机器人早晨起床流程
"""

import py_trees
import random
from datetime import datetime


# ==================== 基础行为节点 ====================

class IsAlarmRinging(py_trees.behaviour.Behaviour):
    """检查闹钟是否响了（随机返回成功或失败）"""

    def __init__(self, name="Is Alarm Ringing?"):
        super(IsAlarmRinging, self).__init__(name)

    def update(self):
        # 70% 概率闹钟响了
        if random.random() < 0.7:
            self.feedback_message = "⏰ Alarm is ringing!"
            print(f"✓ {self.feedback_message}")
            return py_trees.common.Status.SUCCESS
        else:
            self.feedback_message = "😴 Alarm not ringing yet..."
            print(f"✗ {self.feedback_message}")
            return py_trees.common.Status.FAILURE


class HitSnoozeButton(py_trees.behaviour.Behaviour):
    """按掉闹钟继续睡"""

    def __init__(self, name="Hit Snooze"):
        super(HitSnoozeButton, self).__init__(name)

    def update(self):
        print("💤 Snoozing... ZZZ")
        return py_trees.common.Status.SUCCESS


class GetOutOfBed(py_trees.behaviour.Behaviour):
    """起床"""

    def __init__(self, name="Get Out of Bed"):
        super(GetOutOfBed, self).__init__(name)

    def update(self):
        print("🛏️  Getting up!")
        return py_trees.common.Status.SUCCESS


class BrewCoffee(py_trees.behaviour.Behaviour):
    """冲咖啡"""

    def __init__(self, name="Brew Coffee"):
        super(BrewCoffee, self).__init__(name)

    def update(self):
        print("☕ Brewing coffee...")
        return py_trees.common.Status.SUCCESS


# ==================== 新增：工作日检查节点 ====================

class IsWeekday(py_trees.behaviour.Behaviour):
    """检查是否为工作日（周一到周五）"""

    def __init__(self, name="Is Weekday?"):
        super(IsWeekday, self).__init__(name)

    def update(self):
        # 0=Monday, 6=Sunday
        weekday = datetime.now().weekday()

        if weekday < 5:  # Monday to Friday
            day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][weekday]
            self.feedback_message = f"📅 Today is {day_name} (Weekday)"
            print(f"✓ {self.feedback_message}")
            return py_trees.common.Status.SUCCESS
        else:
            day_name = "Saturday" if weekday == 5 else "Sunday"
            self.feedback_message = f"📅 Today is {day_name} (Weekend)"
            print(f"✗ {self.feedback_message}")
            return py_trees.common.Status.FAILURE


class StartWork(py_trees.behaviour.Behaviour):
    """开始工作"""

    def __init__(self, name="Start Work"):
        super(StartWork, self).__init__(name)

    def update(self):
        print("💼 Starting work...")
        return py_trees.common.Status.SUCCESS


class RelaxOnWeekend(py_trees.behaviour.Behaviour):
    """周末放松"""

    def __init__(self, name="Relax on Weekend"):
        super(RelaxOnWeekend, self).__init__(name)

    def update(self):
        print("🏖️  Relaxing on the weekend!")
        return py_trees.common.Status.SUCCESS


# ==================== 构建行为树 ====================

def create_behavior_tree():
    """
    创建机器人早晨例程行为树

    树结构:
    Root (Sequence)
    ├── Wake Up Routine (Selector)
    │   ├── Snooze Sequence (Sequence)
    │   │   ├── Is Alarm Ringing?
    │   │   └── Hit Snooze
    │   └── Get Out of Bed
    ├── Morning Preparation (Sequence) - 仅工作日冲咖啡
    │   ├── Weekday Coffee (Selector)
    │   │   ├── Weekday Coffee Sequence (Sequence)
    │   │   │   ├── Is Weekday?
    │   │   │   └── Brew Coffee
    │   │   └── Skip Coffee (Success)
    └── Start Day (Selector)
        ├── Work Sequence (Sequence)
        │   ├── Is Weekday?
        │   └── Start Work
        └── Relax on Weekend
    """

    # 根节点：整个早晨流程必须顺序执行
    root = py_trees.composites.Sequence(
        name="Morning Routine",
        memory=False
    )

    # ===== 第一部分：起床流程 (使用 Selector) =====
    # Selector: 尝试第一个子节点，失败则尝试第二个
    wake_up = py_trees.composites.Selector(
        name="Wake Up Routine",
        memory=False
    )

    # 贪睡分支：如果闹钟响了就按掉继续睡 (Sequence)
    snooze_sequence = py_trees.composites.Sequence(
        name="Snooze Sequence",
        memory=False
    )
    snooze_sequence.add_children([
        IsAlarmRinging(),
        HitSnoozeButton()
    ])

    # Selector的逻辑：先尝试贪睡，如果闹钟没响（失败），则执行起床
    wake_up.add_children([
        snooze_sequence,
        GetOutOfBed()
    ])

    # ===== 第二部分：早晨准备 - 仅工作日冲咖啡 (使用 Selector) =====
    morning_prep = py_trees.composites.Sequence(
        name="Morning Preparation",
        memory=False
    )

    # 工作日咖啡逻辑：使用Selector来处理"仅工作日冲咖啡"
    weekday_coffee = py_trees.composites.Selector(
        name="Weekday Coffee",
        memory=False
    )

    # 工作日咖啡序列
    coffee_on_weekday = py_trees.composites.Sequence(
        name="Weekday Coffee Sequence",
        memory=False
    )
    coffee_on_weekday.add_children([
        IsWeekday(),
        BrewCoffee()
    ])

    # 总是成功的节点（用于周末跳过咖啡）
    skip_coffee = py_trees.behaviours.Success(name="Skip Coffee on Weekend")

    # Selector逻辑：先检查是否工作日并冲咖啡，失败则跳过（周末）
    weekday_coffee.add_children([
        coffee_on_weekday,
        skip_coffee
    ])

    morning_prep.add_children([weekday_coffee])

    # ===== 第三部分：开始一天 (使用 Selector) =====
    start_day = py_trees.composites.Selector(
        name="Start Day",
        memory=False
    )

    # 工作日工作序列
    work_sequence = py_trees.composites.Sequence(
        name="Work Sequence",
        memory=False
    )
    work_sequence.add_children([
        IsWeekday(),
        StartWork()
    ])

    # Selector逻辑：工作日就工作，周末就放松
    start_day.add_children([
        work_sequence,
        RelaxOnWeekend()
    ])

    # 组装完整的树
    root.add_children([
        wake_up,
        morning_prep,
        start_day
    ])

    return root


# ==================== 主程序 ====================

def main():
    """运行机器人早晨例程行为树"""

    print("=" * 60)
    print("🤖 Robot's Morning Routine Behavior Tree")
    print("=" * 60)
    print()

    # 创建行为树
    bt = create_behavior_tree()

    # 设置行为树
    bt.setup_with_descendants()

    # 打印行为树结构
    print("📋 Behavior Tree Structure:")
    print(py_trees.display.unicode_tree(bt, show_status=True))
    print()

    # 执行行为树（执行多次以展示不同情况）
    print("🚀 Executing Behavior Tree:")
    print("-" * 60)

    for i in range(3):
        print(f"\n▶️  Execution #{i + 1}")
        print("-" * 40)
        bt.tick_once()
        print()

    print("=" * 60)
    print("✅ Robot's morning routine completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
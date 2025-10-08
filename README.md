如何运行
环境要求

Python 3.7+
py_trees 库

安装依赖
bashpip install py_trees
运行程序
bashpython robot_morning_routine.py
程序会执行 3 次行为树，每次都可能产生不同的结果（因为闹钟是否响起是随机的）。
🌳 行为树结构
MorningRoutine (Sequence) - 根节点
│
├── AlarmResponse (Selector) - 响应闹钟
│   ├── WakeUpSequence (Sequence) - 醒来并起床
│   │   ├── IsAlarmRinging - 检查闹钟是否响
│   │   └── GetOutOfBed - 起床
│   └── HitSnoozeButton - 继续睡（闹钟未响时）
│
└── MorningPreparation (Sequence) - 早晨准备
    ├── WeekdayCheck (Selector) - 检查是否需要冲咖啡
    │   ├── WorkdayRoutine (Sequence) - 工作日流程
    │   │   ├── IsWeekday - 检查是否工作日
    │   │   └── BrewCoffee - 冲咖啡
    │   └── WeekendRoutine (Sequence) - 周末流程
    │       └── SkipCoffee (Success) - 跳过咖啡
    └── DayStart (Selector) - 开始一天
        ├── WorkdayStart (Sequence) - 工作日开始
        │   ├── IsWeekday - 再次检查工作日
        │   └── StartWorkday - 开始工作
        └── EnjoyWeekend - 享受周末
树结构可视化图
          [ROOT]
     MorningRoutine
            |
    +-------+-------+
    |               |
AlarmResponse  MorningPrep
(Selector)     (Sequence)
    |               |
    +---+---+   +---+---+
    |       |   |       |
  Wake   Snooze Week  Day
  (Seq)        Check  Start
    |         (Sel)  (Sel)
  +-+-+         |      |
  | | |      +--+--+ +-+--+
  A G |      W  W   W    E
  l e |      o  e   o    n
  a t |      r  e   r    j
  r O |      k  k   k    o
  m u |      d  e   d    y
  i t |      a  n   a
  n   |      y  d   y
  g   |
💡 设计说明
Sequence 的使用
在哪里使用了 Sequence？

MorningRoutine (根节点)

位置: 最顶层
原因: 早晨流程必须按顺序执行：先处理闹钟，再进行早晨准备。这是一个严格的顺序依赖关系。


WakeUpSequence

位置: AlarmResponse 的第一个子节点
原因: 只有当闹钟响了（IsAlarmRinging 成功）之后，机器人才能起床（GetOutOfBed）。这是一个条件-动作的顺序关系。


WorkdayRoutine

位置: WeekdayCheck 的第一个子节点
原因: 必须先确认是工作日（IsWeekday 成功），然后才执行冲咖啡（BrewCoffee）。这保证了咖啡只在工作日冲泡。


WorkdayStart

位置: DayStart 的第一个子节点
原因: 同样需要先确认是工作日，再开始工作。



Sequence 的特点: 所有子节点必须依次成功执行，任何一个失败则整个 Sequence 失败。
Selector 的使用
在哪里使用了 Selector？

AlarmResponse

位置: 根节点的第一个子节点
原因: 机器人需要"选择"一种响应方式：

如果闹钟响了，就起床（WakeUpSequence 成功）
如果闹钟没响，就继续睡（HitSnoozeButton 执行）


这是一个"二选一"的决策逻辑。


WeekdayCheck

位置: MorningPreparation 的第一个子节点
原因: 根据是否工作日选择不同的行为：

工作日：执行 WorkdayRoutine（检查 + 冲咖啡）
周末：执行 WeekendRoutine（直接跳过）


这确保了系统总能找到一条成功的路径。


DayStart

位置: MorningPreparation 的第二个子节点
原因: 根据日期类型开始不同的一天：

工作日：开始工作
周末：享受休闲时光





Selector 的特点: 依次尝试子节点，直到有一个成功，则 Selector 成功。如果所有子节点都失败，Selector 才失败。
为什么这样设计？

Sequence: 用于必须按顺序发生的事情（起床→准备→开始一天）
Selector: 用于决策分支（响应闹钟的方式、工作日vs周末的不同行为）

这种组合使得行为树既有明确的流程，又有灵活的决策能力。
🤔 思考题：仅在工作日冲咖啡
问题
如果现在要增加一个条件"仅在工作日冲咖啡"，你会在行为树的哪个部分进行修改？
实现方案
已在代码中实现！ 相关代码位置：第 138-167 行
实现细节

新增了 IsWeekday 节点（第 68-87 行）

python   class IsWeekday(py_trees.behaviour.Behaviour):
       def update(self):
           weekday = datetime.now().weekday()
           if weekday < 5:  # 周一到周五
               return py_trees.common.Status.SUCCESS
           else:
               return py_trees.common.Status.FAILURE

创建了 WeekdayCheck Selector（第 138-167 行）

python   weekday_check = py_trees.composites.Selector(
       name="WeekdayCheck",
       memory=False
   )

工作日流程 (使用 Sequence)

python   workday_routine = py_trees.composites.Sequence(
       name="WorkdayRoutine",
       memory=False
   )
   workday_routine.add_children([
       IsWeekday(),      # 先检查是否工作日
       BrewCoffee()      # 如果是，才冲咖啡
   ])

周末流程 (直接成功，跳过咖啡)

python   weekend_routine = py_trees.composites.Sequence(
       name="WeekendRoutine",
       memory=False
   )
   weekend_routine.add_child(
       py_trees.behaviours.Success(name="SkipCoffee")
   )

组合到 Selector 中

python   weekday_check.add_children([
       workday_routine,   # 尝试工作日流程
       weekend_routine    # 如果不是工作日，执行周末流程
   ])
设计理念
使用 Selector + Sequence 的组合：

Selector 负责"选择"走哪条路径（工作日 vs 周末）
Sequence 确保条件检查和行为执行的顺序性
如果不是工作日，WorkdayRoutine 的 IsWeekday 会失败，Selector 会尝试下一个子节点（周末流程），保证树不会因为不冲咖啡而失败

运行效果

工作日（周一-周五）：会看到 "✅ 今天是工作日" → "☕ Brewing coffee..."
周末（周六-周日）：会看到 "❌ 今天是周末" → 跳过咖啡，直接进入下一个流程

📊 示例输出
🤖 机器人早晨起床流程 - 行为树演示
============================================================

📊 行为树结构:
[显示完整的树结构]

▶️  开始执行行为树...
------------------------------------------------------------

【第 1 次执行】
============================================================
[IsAlarmRinging] ⏰ 闹钟响了！
[GetOutOfBed] 🛏️  Getting up! 起床了！
[IsWeekday] ✅ 今天是工作日 (星期1)
[BrewCoffee] ☕ Brewing coffee... 正在冲咖啡
[IsWeekday] ✅ 今天是工作日 (星期1)
[StartWorkday] 💼 开始一天的工作！
------------------------------------------------------------
执行结果: Status.SUCCESS
节点类型	                  功能	                        示例
行为节点（Behaviour）	实际执行某个动作或检查条件	       “起床”“冲咖啡”“检查是否工作日”
序列（Sequence）	 顺序执行所有子节点，只有全部成功才成功	“起床流程”：先闹钟响，再起床
选择器（Selector）	尝试每个子节点，直到一个成功就停止  	“要么工作，要么休息”
装饰器（Decorator）	修改子节点的返回值（此例未用）	         重复执行、反转逻辑等

整个流程由三个阶段组成：
Wake Up Routine（起床流程）
Morning Preparation（早晨准备）
Start Day（开始一天）

环境要求
Python 3.7+
py_trees 库
安装依赖
pip install py_trees
运行程序
python robot_morning_routine.py

符号	含义	                                                            来源
[-]	    表示 复合节点 (Composite Node)，例如 Sequence 或 Selector	          py_trees.display.unicode_tree()
[o]	    也是复合节点，通常代表“开放状态 (open)”的 Selector（或内含状态的节点）	同上
-->	     表示 子节点 (Child Behaviour)	                                    同上

行为树结构
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

 思考题：
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


在哪里使用了 Selector？
AlarmResponse
位置: 根节点的第一个子节点
原因: 机器人需要"选择"一种响应方式：
如果闹钟响了，就起床（WakeUpSequence 成功）
如果闹钟没响，就继续睡（HitSnoozeButton 执行）
WeekdayCheck
位置: MorningPreparation 的第一个子节点
原因: 根据是否工作日选择不同的行为：
工作日：执行 WorkdayRoutine（检查 + 冲咖啡）
周末：执行 WeekendRoutine（直接跳过）
DayStart
位置: MorningPreparation 的第二个子节点
原因: 根据日期类型开始不同的一天：
工作日：开始工作
周末：享受休闲时光
Sequence: 用于必须按顺序发生的事情（起床→准备→开始一天）
Selector: 用于决策分支（响应闹钟的方式、工作日vs周末的不同行为）


思考题：仅在工作日冲咖啡
如果现在要增加一个条件"仅在工作日冲咖啡"，你会在行为树的哪个部分进行修改？
新增了 IsWeekday 节点
python   class IsWeekday(py_trees.behaviour.Behaviour):
       def update(self):
           weekday = datetime.now().weekday()
           if weekday < 5:  # 周一到周五
               return py_trees.common.Status.SUCCESS
           else:
               return py_trees.common.Status.FAILURE

创建了 WeekdayCheck Selector

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
使用 Selector + Sequence 的组合：
Selector 负责"选择"走哪条路径（工作日 vs 周末）
Sequence 确保条件检查和行为执行的顺序性
如果不是工作日，WorkdayRoutine 的 IsWeekday 会失败，Selector 会尝试下一个子节点（周末流程），保证树不会因为不冲咖啡而失败

运行效果
工作日（周一-周五）：会看到 " 今天是工作日" → " Brewing coffee..."
周末（周六-周日）：会看到 "今天是周末" → 跳过咖啡，直接进入下一个流程



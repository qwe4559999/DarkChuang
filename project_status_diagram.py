import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# 定义颜色
color_problem = '#FF6B6B'  # 红色 - 问题
color_solution = '#4ECDC4'  # 青色 - 解决方案
color_plan = '#45B7D1'     # 蓝色 - 计划
color_milestone = '#96CEB4' # 绿色 - 里程碑

# 标题
ax.text(5, 9.5, 'DarkChuang 项目状态图谱', fontsize=24, fontweight='bold', ha='center')

# 第一部分：当前问题
problems_box = FancyBboxPatch((0.5, 7.5), 2.2, 1.5, 
                             boxstyle="round,pad=0.1", 
                             facecolor=color_problem, alpha=0.3, 
                             edgecolor=color_problem, linewidth=2)
ax.add_patch(problems_box)
ax.text(1.6, 8.7, '当前问题', fontsize=16, fontweight='bold', ha='center')
problems = [
    '◆ 依赖环境不完整',
    '◆ 知识库建设滞后', 
    '◆ API数据验证缺失'
]
for i, problem in enumerate(problems):
    ax.text(0.6, 8.4-i*0.2, problem, fontsize=11, ha='left')

# 第二部分：解决方案
solutions_box = FancyBboxPatch((2.9, 7.5), 2.2, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor=color_solution, alpha=0.3,
                              edgecolor=color_solution, linewidth=2)
ax.add_patch(solutions_box)
ax.text(4.0, 8.7, '解决方案', fontsize=16, fontweight='bold', ha='center')
solutions = [
    '◆ 完善依赖安装脚本',
    '◆ 建立化学知识库',
    '◆ 优化API响应处理'
]
for i, solution in enumerate(solutions):
    ax.text(3.0, 8.4-i*0.2, solution, fontsize=11, ha='left')

# 第三部分：下一步计划
plan_box = FancyBboxPatch((5.3, 7.5), 2.2, 1.5,
                         boxstyle="round,pad=0.1",
                         facecolor=color_plan, alpha=0.3,
                         edgecolor=color_plan, linewidth=2)
ax.add_patch(plan_box)
ax.text(6.4, 8.7, '下一步计划', fontsize=16, fontweight='bold', ha='center')
plans = [
    '◆ 短期：修复核心问题',
    '◆ 中期：功能完善',
    '◆ 长期：生态建设'
]
for i, plan in enumerate(plans):
    ax.text(5.4, 8.4-i*0.2, plan, fontsize=11, ha='left')

# 第四部分：关键里程碑
milestone_box = FancyBboxPatch((7.7, 7.5), 2.2, 1.5,
                              boxstyle="round,pad=0.1",
                              facecolor=color_milestone, alpha=0.3,
                              edgecolor=color_milestone, linewidth=2)
ax.add_patch(milestone_box)
ax.text(8.8, 8.7, '关键里程碑', fontsize=16, fontweight='bold', ha='center')
milestones = [
    '◆ 基础功能稳定',
    '◆ 知识库上线',
    '◆ 用户体验优化'
]
for i, milestone in enumerate(milestones):
    ax.text(7.8, 8.4-i*0.2, milestone, fontsize=11, ha='left')

# 添加箭头连接
arrow1 = patches.FancyArrowPatch((2.7, 8.2), (2.9, 8.2),
                                arrowstyle='->', mutation_scale=20,
                                color='gray', linewidth=2)
ax.add_patch(arrow1)

arrow2 = patches.FancyArrowPatch((5.1, 8.2), (5.3, 8.2),
                                arrowstyle='->', mutation_scale=20,
                                color='gray', linewidth=2)
ax.add_patch(arrow2)

arrow3 = patches.FancyArrowPatch((7.5, 8.2), (7.7, 8.2),
                                arrowstyle='->', mutation_scale=20,
                                color='gray', linewidth=2)
ax.add_patch(arrow3)

# 详细时间线
ax.text(5, 6.8, '项目时间线规划', fontsize=18, fontweight='bold', ha='center')

# 短期目标 (1-2周)
short_term_box = FancyBboxPatch((0.5, 5.5), 3.0, 1,
                               boxstyle="round,pad=0.1",
                               facecolor='#FFE5E5', alpha=0.8,
                               edgecolor=color_problem, linewidth=1)
ax.add_patch(short_term_box)
ax.text(2.0, 6.2, '短期目标 (1-2周)', fontsize=14, fontweight='bold', ha='center')
short_goals = [
    '1. 修复依赖问题，确保环境稳定',
    '2. 完善错误处理和日志记录',
    '3. 建立基础化学知识库'
]
for i, goal in enumerate(short_goals):
    ax.text(0.6, 5.9-i*0.15, goal, fontsize=10, ha='left')

# 中期目标 (1-2月)
mid_term_box = FancyBboxPatch((3.7, 5.5), 3.0, 1,
                             boxstyle="round,pad=0.1",
                             facecolor='#E5F9F6', alpha=0.8,
                             edgecolor=color_solution, linewidth=1)
ax.add_patch(mid_term_box)
ax.text(5.2, 6.2, '中期目标 (1-2月)', fontsize=14, fontweight='bold', ha='center')
mid_goals = [
    '1. 完善光谱分析功能',
    '2. 优化用户界面体验',
    '3. 扩展知识库内容'
]
for i, goal in enumerate(mid_goals):
    ax.text(3.8, 5.9-i*0.15, goal, fontsize=10, ha='left')

# 长期目标 (3-6月)
long_term_box = FancyBboxPatch((6.9, 5.5), 3.0, 1,
                              boxstyle="round,pad=0.1",
                              facecolor='#E5F3FF', alpha=0.8,
                              edgecolor=color_plan, linewidth=1)
ax.add_patch(long_term_box)
ax.text(8.4, 6.2, '长期目标 (3-6月)', fontsize=14, fontweight='bold', ha='center')
long_goals = [
    '1. 实现多模态分析能力',
    '2. 建立用户系统推荐',
    '3. 开发移动端和API生态'
]
for i, goal in enumerate(long_goals):
    ax.text(7.0, 5.9-i*0.15, goal, fontsize=10, ha='left')

# 技术架构优化路径
ax.text(5, 4.8, '技术架构优化路径', fontsize=18, fontweight='bold', ha='center')

# 创建技术路径图
tech_boxes = [
    {'pos': (1, 3.8), 'text': '环境\n稳定化', 'color': color_problem},
    {'pos': (3, 3.8), 'text': '知识库\n建设', 'color': color_solution},
    {'pos': (5, 3.8), 'text': '功能\n完善', 'color': color_plan},
    {'pos': (7, 3.8), 'text': '性能\n优化', 'color': color_milestone},
    {'pos': (9, 3.8), 'text': '生态\n扩展', 'color': '#F39C12'}
]

for i, box in enumerate(tech_boxes):
    tech_box = FancyBboxPatch((box['pos'][0]-0.4, box['pos'][1]-0.3), 0.8, 0.6,
                             boxstyle="round,pad=0.05",
                             facecolor=box['color'], alpha=0.3,
                             edgecolor=box['color'], linewidth=2)
    ax.add_patch(tech_box)
    ax.text(box['pos'][0], box['pos'][1], box['text'], 
           fontsize=12, fontweight='bold', ha='center', va='center')
    
    # 添加连接箭头
    if i < len(tech_boxes) - 1:
        arrow = patches.FancyArrowPatch(
            (box['pos'][0]+0.4, box['pos'][1]), 
            (tech_boxes[i+1]['pos'][0]-0.4, tech_boxes[i+1]['pos'][1]),
            arrowstyle='->', mutation_scale=15,
            color='gray', linewidth=1.5
        )
        ax.add_patch(arrow)

# 创新亮点
innovation_box = FancyBboxPatch((0.5, 0.5), 9, 1.2,
                               boxstyle="round,pad=0.1",
                               facecolor='#FFF9E5', alpha=0.8,
                               edgecolor='#F39C12', linewidth=2)
ax.add_patch(innovation_box)
ax.text(5, 1.4, '创新亮点规划', fontsize=16, fontweight='bold', ha='center')
innovations = [
    '◆ 多模态化学分析：结合文本、图像、光谱数据的综合分析能力',
    '◆ 智能知识图谱：构建化学实体关系网络，支持复杂查询推理',
    '◆ 个性化学习：基于用户行为的智能推荐和学习路径规划'
]
for i, innovation in enumerate(innovations):
    ax.text(0.7, 1.1-i*0.15, innovation, fontsize=11, ha='left')

plt.tight_layout()
plt.savefig('d:\\document\\DarkChuang\\project_status_diagram.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

print("项目状态图谱已生成：project_status_diagram.png")
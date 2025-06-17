#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
化学问答机器人项目架构图生成器
生成清晰美观的项目架构图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# 设置中文字体和解决字体缺失问题
try:
    # 尝试使用系统中可用的中文字体
    import matplotlib.font_manager as fm
    # 获取系统字体列表
    font_list = [f.name for f in fm.fontManager.ttflist]
    
    # 按优先级选择可用字体
    preferred_fonts = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans', 'Arial']
    selected_font = 'DejaVu Sans'  # 默认字体
    
    for font in preferred_fonts:
        if font in font_list:
            selected_font = font
            break
    
    plt.rcParams['font.sans-serif'] = [selected_font]
    plt.rcParams['axes.unicode_minus'] = False
    print(f"使用字体: {selected_font}")
except Exception as e:
    print(f"字体设置警告: {e}")
    # 使用默认字体
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

def create_architecture_diagram():
    """创建项目架构图"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 定义颜色方案
    colors = {
        'frontend': '#4A90E2',      # 蓝色
        'backend': '#7ED321',       # 绿色
        'ai': '#F5A623',            # 橙色
        'database': '#D0021B',      # 红色
        'deployment': '#9013FE',    # 紫色
        'user': '#50E3C2'           # 青色
    }
    
    # 标题
    ax.text(5, 9.5, 'DarkChuang Chemistry Q&A System Architecture', 
            fontsize=20, fontweight='bold', ha='center')
    
    # 用户层
    user_box = FancyBboxPatch((0.5, 8), 9, 0.8, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['user'], 
                              edgecolor='black', 
                              alpha=0.8)
    ax.add_patch(user_box)
    ax.text(5, 8.4, 'User Interface Layer', 
            fontsize=14, fontweight='bold', ha='center')
    ax.text(2, 8.15, '• Web Browser', fontsize=10, ha='left')
    ax.text(5, 8.15, '• Mobile Device', fontsize=10, ha='center')
    ax.text(8, 8.15, '• API Client', fontsize=10, ha='right')
    
    # 前端层
    frontend_box = FancyBboxPatch((0.5, 6.5), 4, 1.2, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=colors['frontend'], 
                                  edgecolor='black', 
                                  alpha=0.8)
    ax.add_patch(frontend_box)
    ax.text(2.5, 7.4, 'Frontend Layer', 
            fontsize=14, fontweight='bold', ha='center', color='white')
    ax.text(2.5, 7.1, 'SvelteKit + TypeScript', fontsize=11, ha='center', color='white')
    ax.text(1, 6.85, '• Responsive UI', fontsize=9, ha='left', color='white')
    ax.text(1, 6.65, '• Spectrum Analysis', fontsize=9, ha='left', color='white')
    ax.text(3, 6.85, '• API Documentation', fontsize=9, ha='left', color='white')
    ax.text(3, 6.65, '• Real-time Chat', fontsize=9, ha='left', color='white')
    
    # 后端层
    backend_box = FancyBboxPatch((5.5, 6.5), 4, 1.2, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=colors['backend'], 
                                 edgecolor='black', 
                                 alpha=0.8)
    ax.add_patch(backend_box)
    ax.text(7.5, 7.4, 'Backend Layer', 
            fontsize=14, fontweight='bold', ha='center', color='white')
    ax.text(7.5, 7.1, 'FastAPI + Python', fontsize=11, ha='center', color='white')
    ax.text(6, 6.85, '• RESTful API', fontsize=9, ha='left', color='white')
    ax.text(6, 6.65, '• Async Processing', fontsize=9, ha='left', color='white')
    ax.text(8, 6.85, '• File Upload', fontsize=9, ha='left', color='white')
    ax.text(8, 6.65, '• Data Validation', fontsize=9, ha='left', color='white')
    
    # AI模型层
    ai_box = FancyBboxPatch((1, 4.5), 8, 1.5, 
                            boxstyle="round,pad=0.1", 
                            facecolor=colors['ai'], 
                            edgecolor='black', 
                            alpha=0.8)
    ax.add_patch(ai_box)
    ax.text(5, 5.7, 'AI Models Layer', 
            fontsize=14, fontweight='bold', ha='center', color='white')
    
    # AI子模块
    # 视觉模型
    vision_box = FancyBboxPatch((1.5, 4.8), 2.5, 0.6, 
                                boxstyle="round,pad=0.05", 
                                facecolor='white', 
                                edgecolor='black', 
                                alpha=0.9)
    ax.add_patch(vision_box)
    ax.text(2.75, 5.2, 'Vision Model', fontsize=11, fontweight='bold', ha='center')
    ax.text(2.75, 4.95, 'Qwen2.5-VL-72B', fontsize=9, ha='center')
    
    # 文本模型
    text_box = FancyBboxPatch((4.5, 4.8), 2.5, 0.6, 
                              boxstyle="round,pad=0.05", 
                              facecolor='white', 
                              edgecolor='black', 
                              alpha=0.9)
    ax.add_patch(text_box)
    ax.text(5.75, 5.2, 'Text Model', fontsize=11, fontweight='bold', ha='center')
    ax.text(5.75, 4.95, 'DeepSeek-R1', fontsize=9, ha='center')
    
    # RAG系统
    rag_box = FancyBboxPatch((7.5, 4.8), 1.2, 0.6, 
                             boxstyle="round,pad=0.05", 
                             facecolor='white', 
                             edgecolor='black', 
                             alpha=0.9)
    ax.add_patch(rag_box)
    ax.text(8.1, 5.2, 'RAG', fontsize=11, fontweight='bold', ha='center')
    ax.text(8.1, 4.95, 'LangChain', fontsize=9, ha='center')
    
    # 数据层
    data_box = FancyBboxPatch((0.5, 2.5), 9, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['database'], 
                              edgecolor='black', 
                              alpha=0.8)
    ax.add_patch(data_box)
    ax.text(5, 3.7, 'Data Layer', 
            fontsize=14, fontweight='bold', ha='center', color='white')
    
    # 数据子模块
    # 向量数据库
    vector_box = FancyBboxPatch((1, 2.8), 2.5, 0.6, 
                                boxstyle="round,pad=0.05", 
                                facecolor='white', 
                                edgecolor='black', 
                                alpha=0.9)
    ax.add_patch(vector_box)
    ax.text(2.25, 3.2, 'Vector Database', fontsize=11, fontweight='bold', ha='center')
    ax.text(2.25, 2.95, 'ChromaDB', fontsize=9, ha='center')
    
    # 文件存储
    file_box = FancyBboxPatch((4, 2.8), 2, 0.6, 
                              boxstyle="round,pad=0.05", 
                              facecolor='white', 
                              edgecolor='black', 
                              alpha=0.9)
    ax.add_patch(file_box)
    ax.text(5, 3.2, 'File Storage', fontsize=11, fontweight='bold', ha='center')
    ax.text(5, 2.95, 'Uploads/Logs', fontsize=9, ha='center')
    
    # 知识库
    knowledge_box = FancyBboxPatch((6.5, 2.8), 2.5, 0.6, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor='white', 
                                   edgecolor='black', 
                                   alpha=0.9)
    ax.add_patch(knowledge_box)
    ax.text(7.75, 3.2, 'Knowledge Base', fontsize=11, fontweight='bold', ha='center')
    ax.text(7.75, 2.95, 'Books/Papers/Images', fontsize=9, ha='center')
    
    # 部署层
    deploy_box = FancyBboxPatch((0.5, 0.5), 9, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['deployment'], 
                                edgecolor='black', 
                                alpha=0.8)
    ax.add_patch(deploy_box)
    ax.text(5, 1.7, 'Deployment Layer', 
            fontsize=14, fontweight='bold', ha='center', color='white')
    
    # 部署子模块
    docker_box = FancyBboxPatch((1.5, 0.8), 2.5, 0.6, 
                                boxstyle="round,pad=0.05", 
                                facecolor='white', 
                                edgecolor='black', 
                                alpha=0.9)
    ax.add_patch(docker_box)
    ax.text(2.75, 1.2, 'Docker Container', fontsize=11, fontweight='bold', ha='center')
    ax.text(2.75, 0.95, 'Docker Compose', fontsize=9, ha='center')
    
    nginx_box = FancyBboxPatch((4.5, 0.8), 2, 0.6, 
                               boxstyle="round,pad=0.05", 
                               facecolor='white', 
                               edgecolor='black', 
                               alpha=0.9)
    ax.add_patch(nginx_box)
    ax.text(5.5, 1.2, 'Reverse Proxy', fontsize=11, fontweight='bold', ha='center')
    ax.text(5.5, 0.95, 'Nginx', fontsize=9, ha='center')
    
    monitor_box = FancyBboxPatch((7, 0.8), 2, 0.6, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='white', 
                                 edgecolor='black', 
                                 alpha=0.9)
    ax.add_patch(monitor_box)
    ax.text(8, 1.2, 'Monitoring', fontsize=11, fontweight='bold', ha='center')
    ax.text(8, 0.95, 'Auto Scripts', fontsize=9, ha='center')
    
    # 添加连接线
    # 用户到前端
    ax.arrow(2.5, 8, 0, -0.2, head_width=0.1, head_length=0.05, fc='black', ec='black')
    ax.arrow(7.5, 8, 0, -0.2, head_width=0.1, head_length=0.05, fc='black', ec='black')
    
    # 前端到后端
    ax.arrow(4.5, 7.1, 1, 0, head_width=0.1, head_length=0.1, fc='black', ec='black')
    
    # 后端到AI
    ax.arrow(7.5, 6.5, 0, -0.4, head_width=0.1, head_length=0.05, fc='black', ec='black')
    ax.arrow(2.5, 6.5, 0, -0.4, head_width=0.1, head_length=0.05, fc='black', ec='black')
    
    # AI到数据
    ax.arrow(5, 4.5, 0, -0.4, head_width=0.1, head_length=0.05, fc='black', ec='black')
    
    # 数据到部署
    ax.arrow(5, 2.5, 0, -0.4, head_width=0.1, head_length=0.05, fc='black', ec='black')
    
    # 添加技术特色标注
    ax.text(0.2, 5.5, 'Dual Model\nCollaboration', fontsize=10, ha='center', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    ax.text(9.8, 3.5, 'RAG\nEnhancement', fontsize=10, ha='center', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    return fig

def create_data_flow_diagram():
    """创建数据流程图"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # 标题
    ax.text(6, 7.5, 'DarkChuang Data Flow Diagram', 
            fontsize=18, fontweight='bold', ha='center')
    
    # 定义流程步骤
    steps = [
        {'pos': (1, 6), 'size': (1.5, 0.8), 'text': 'User Input\n(Text/Image)', 'color': '#4A90E2'},
        {'pos': (3.5, 6), 'size': (1.5, 0.8), 'text': 'Frontend\nValidation', 'color': '#4A90E2'},
        {'pos': (6, 6), 'size': (1.5, 0.8), 'text': 'API Router\nDispatch', 'color': '#7ED321'},
        {'pos': (8.5, 6), 'size': (2, 0.8), 'text': 'Service Layer\nBusiness Logic', 'color': '#7ED321'},
        
        {'pos': (1, 4), 'size': (2, 0.8), 'text': 'Image Recognition\nQwen2.5-VL', 'color': '#F5A623'},
        {'pos': (4, 4), 'size': (2, 0.8), 'text': 'Text Analysis\nDeepSeek-R1', 'color': '#F5A623'},
        {'pos': (7.5, 4), 'size': (2, 0.8), 'text': 'RAG Retrieval\nLangChain', 'color': '#F5A623'},
        
        {'pos': (2.5, 2), 'size': (2, 0.8), 'text': 'Vector Database\nChromaDB', 'color': '#D0021B'},
        {'pos': (6.5, 2), 'size': (2.5, 0.8), 'text': 'Knowledge Base\nChemistry Docs', 'color': '#D0021B'},
        
        {'pos': (5, 0.5), 'size': (2, 0.8), 'text': 'Result Return\nStructured Output', 'color': '#50E3C2'}
    ]
    
    # 绘制步骤框
    for step in steps:
        box = FancyBboxPatch(step['pos'], step['size'][0], step['size'][1], 
                             boxstyle="round,pad=0.1", 
                             facecolor=step['color'], 
                             edgecolor='black', 
                             alpha=0.8)
        ax.add_patch(box)
        ax.text(step['pos'][0] + step['size'][0]/2, 
                step['pos'][1] + step['size'][1]/2, 
                step['text'], 
                fontsize=10, fontweight='bold', ha='center', va='center',
                color='white' if step['color'] != '#50E3C2' else 'black')
    
    # 添加箭头连接
    arrows = [
        ((2.5, 6.4), (3.5, 6.4)),  # 用户输入 -> 前端处理
        ((5, 6.4), (6, 6.4)),      # 前端处理 -> API路由
        ((7.5, 6.4), (8.5, 6.4)),  # API路由 -> 服务层
        
        ((9.5, 6), (2, 4.8)),      # 服务层 -> 图像识别
        ((9.5, 6), (5, 4.8)),      # 服务层 -> 文本分析
        ((9.5, 6), (8.5, 4.8)),    # 服务层 -> RAG检索
        
        ((2, 4), (3.5, 2.8)),      # 图像识别 -> 向量数据库
        ((5, 4), (3.5, 2.8)),      # 文本分析 -> 向量数据库
        ((8.5, 4), (7.75, 2.8)),   # RAG检索 -> 知识库
        
        ((4.5, 2), (5.5, 1.3)),    # 向量数据库 -> 结果返回
        ((7.75, 2), (6.5, 1.3)),   # 知识库 -> 结果返回
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    plt.tight_layout()
    return fig

def main():
    """Main function"""
    print("Generating project architecture diagrams...")
    
    # 生成架构图
    arch_fig = create_architecture_diagram()
    arch_fig.savefig('DarkChuang_Architecture.png', dpi=300, bbox_inches='tight', 
                     facecolor='white', edgecolor='none')
    print("✅ Architecture diagram saved as: DarkChuang_Architecture.png")
    
    # 生成数据流程图
    flow_fig = create_data_flow_diagram()
    flow_fig.savefig('DarkChuang_DataFlow.png', dpi=300, bbox_inches='tight', 
                     facecolor='white', edgecolor='none')
    print("✅ Data flow diagram saved as: DarkChuang_DataFlow.png")
    
    # 显示图表
    plt.show()
    
    print("\n📊 Architecture diagrams generated successfully!")
    print("Generated files:")
    print("1. DarkChuang_Architecture.png - System Architecture Diagram")
    print("2. DarkChuang_DataFlow.png - Data Flow Diagram")

if __name__ == "__main__":
    main()
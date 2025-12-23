import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

def draw_architecture():
    # Setup figure
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Style constants
    BOX_COLOR_FRONTEND = '#E1F5FE' # Light Blue
    BOX_COLOR_BACKEND = '#E8F5E9'  # Light Green
    BOX_COLOR_DB = '#FFF3E0'       # Light Orange
    BOX_COLOR_EXT = '#F3E5F5'      # Light Purple
    BORDER_COLOR = '#455A64'
    TEXT_COLOR = '#263238'

    def draw_box(x, y, w, h, text, subtext=None, color='#FFFFFF', edge_color=BORDER_COLOR):
        # Shadow
        shadow = patches.FancyBboxPatch((x+0.5, y-0.5), w, h, boxstyle="round,pad=0.5", 
                                      linewidth=0, facecolor='#DDDDDD', zorder=1)
        ax.add_patch(shadow)
        
        # Box
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", 
                                   linewidth=2, edgecolor=edge_color, facecolor=color, zorder=2)
        ax.add_patch(box)
        
        # Text
        ax.text(x + w/2, y + h/2 + (1 if subtext else 0), text, ha='center', va='center', 
                fontsize=12, fontweight='bold', color=TEXT_COLOR, zorder=3)
        if subtext:
            ax.text(x + w/2, y + h/2 - 2, subtext, ha='center', va='center', 
                    fontsize=9, color='#546E7A', zorder=3)
        return (x, y, w, h)

    def draw_arrow(x1, y1, x2, y2, label=None):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#546E7A', 
                                  connectionstyle="arc3,rad=0"), zorder=1)
        if label:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            ax.text(mid_x, mid_y, label, ha='center', va='center', 
                    fontsize=8, backgroundcolor='white', color='#546E7A', zorder=4)

    # --- 1. Frontend Layer (Top) ---
    ax.text(2, 95, "Frontend Layer (Svelte)", ha='left', fontsize=14, fontweight='bold', color='#0277BD')
    
    # User
    draw_box(45, 85, 10, 6, "User", "Browser", color='#B3E5FC')
    
    # Frontend App
    f_x, f_y, f_w, f_h = draw_box(30, 70, 40, 10, "DarkChuang Web App", 
                                 "Svelte + Tailwind + 3Dmol.js + KaTeX", color=BOX_COLOR_FRONTEND)

    # --- 2. Backend Layer (Middle) ---
    ax.text(2, 62, "Backend Layer (FastAPI)", ha='left', fontsize=14, fontweight='bold', color='#2E7D32')
    
    # API Gateway
    api_x, api_y, api_w, api_h = draw_box(30, 45, 40, 12, "FastAPI Server", 
                                         "REST API / WebSocket / Static Files", color=BOX_COLOR_BACKEND)

    # --- 3. Service Layer (Internal) ---
    ax.text(2, 38, "Service Layer", ha='left', fontsize=14, fontweight='bold', color='#455A64')

    # Chemistry Service
    chem_x, chem_y, chem_w, chem_h = draw_box(10, 25, 20, 10, "Chemistry Service", 
                                             "RDKit / Lipinski / SDF", color=BOX_COLOR_BACKEND)
    
    # LLM Service
    llm_x, llm_y, llm_w, llm_h = draw_box(40, 25, 20, 10, "LLM Service", 
                                         "Agent / Prompt Eng.", color=BOX_COLOR_BACKEND)
    
    # RAG Service
    rag_x, rag_y, rag_w, rag_h = draw_box(70, 25, 20, 10, "RAG Service", 
                                         "LangChain / Retrieval", color=BOX_COLOR_BACKEND)

    # --- 4. Data & External Layer (Bottom) ---
    ax.text(2, 2, "Data & Infrastructure", ha='left', fontsize=14, fontweight='bold', color='#EF6C00')

    # SQLite
    sql_x, sql_y, sql_w, sql_h = draw_box(10, 5, 20, 8, "SQLite DB", 
                                         "Chat History / Users", color=BOX_COLOR_DB)
    
    # External LLM
    ext_x, ext_y, ext_w, ext_h = draw_box(40, 5, 20, 8, "Model API", 
                                         "SiliconFlow / GLM-4", color=BOX_COLOR_EXT)
    
    # Vector DB
    vec_x, vec_y, vec_w, vec_h = draw_box(70, 5, 20, 8, "ChromaDB", 
                                         "Vector Embeddings", color=BOX_COLOR_DB)

    # --- Connections ---
    
    # User -> Frontend
    draw_arrow(50, 85, 50, 80.5)
    
    # Frontend -> Backend
    draw_arrow(50, 70, 50, 57.5, "HTTP/JSON")
    
    # Backend -> Services
    draw_arrow(40, 45, 20, 35.5) # To Chem
    draw_arrow(50, 45, 50, 35.5) # To LLM
    draw_arrow(60, 45, 80, 35.5) # To RAG
    
    # Services -> Data
    draw_arrow(20, 25, 20, 13.5, "ORM") # Chem -> SQLite (Implicitly via API, but simplified)
    draw_arrow(50, 25, 50, 13.5, "API Call") # LLM -> API
    draw_arrow(80, 25, 80, 13.5, "Query") # RAG -> Chroma
    
    # Cross Service
    draw_arrow(60, 30, 70, 30, "Context") # LLM -> RAG (Conceptual)

    # Title
    plt.suptitle("DarkChuang System Architecture", fontsize=20, fontweight='bold', y=0.98)
    
    # Save
    output_path = 'project_architecture.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Architecture diagram saved to {output_path}")

if __name__ == "__main__":
    draw_architecture()

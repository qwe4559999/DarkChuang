from typing import Dict, Any, Optional
from rdkit import Chem
from rdkit.Chem import Descriptors, Draw, AllChem
import io
import base64
import uuid
import os
from loguru import logger
import re

class ChemistryService:
    """化学服务 - 提供分子属性计算和可视化功能"""

    def __init__(self):
        pass

    def get_molecule_from_string(self, molecule_string: str) -> Optional[Chem.Mol]:
        """从字符串（SMILES或名称）获取RDKit分子对象"""
        try:
            # 尝试作为SMILES解析
            mol = Chem.MolFromSmiles(molecule_string)
            if mol:
                return mol

            # 如果不是有效的SMILES，尝试作为常用名解析
            # 这里简单支持几个常见的
            common_names = {
                "aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
                "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
                "water": "O",
                "ethanol": "CCO",
                "benzene": "c1ccccc1"
            }

            if molecule_string.lower() in common_names:
                return Chem.MolFromSmiles(common_names[molecule_string.lower()])

            # 优先尝试使用PubChemPy解析名称
            # 这样可以支持更多中文和英文名称
            try:
                import pubchempy as pcp
                logger.info(f"尝试使用PubChemPy解析: {molecule_string}")
                compounds = pcp.get_compounds(molecule_string, 'name')
                if compounds:
                    smiles = compounds[0].isomeric_smiles
                    logger.info(f"PubChemPy解析成功: {molecule_string} -> {smiles}")
                    return Chem.MolFromSmiles(smiles)
            except ImportError:
                logger.warning("PubChemPy未安装，无法从名称解析分子")
            except Exception as e:
                logger.warning(f"PubChemPy解析失败: {str(e)}")

            # 如果本地字典没有，尝试使用PubChemPy（如果安装了）

            logger.warning(f"无法解析分子字符串: {molecule_string}")
            return None

        except Exception as e:
            logger.error(f"解析分子失败: {str(e)}")
            return None

    async def calculate_properties(self, molecule_string: str) -> Dict[str, Any]:
        """计算分子物理化学属性"""
        try:
            mol = self.get_molecule_from_string(molecule_string)
            if not mol:
                return {
                    "success": False,
                    "error": "无效的SMILES或无法识别的分子"
                }

            # 计算属性
            properties = {
                "molecular_weight": round(Descriptors.MolWt(mol), 4),
                "logp": round(Descriptors.MolLogP(mol), 4),
                "h_bond_donors": Descriptors.NumHDonors(mol),
                "h_bond_acceptors": Descriptors.NumHAcceptors(mol),
                "tpsa": round(Descriptors.TPSA(mol), 4),
                "num_rotatable_bonds": Descriptors.NumRotatableBonds(mol),
                "formula": Chem.rdMolDescriptors.CalcMolFormula(mol)
            }

            return {
                "success": True,
                "properties": properties,
                "smiles": Chem.MolToSmiles(mol) # 返回标准化的SMILES
            }

        except Exception as e:
            logger.error(f"计算属性失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_structure_image(self, molecule_string: str, width: int = 400, height: int = 400) -> Dict[str, Any]:
        """生成分子2D结构图"""
        try:
            mol = self.get_molecule_from_string(molecule_string)
            if not mol:
                return {
                    "success": False,
                    "error": "无效的SMILES或无法识别的分子"
                }

            # 生成2D坐标
            AllChem.Compute2DCoords(mol)

            # 绘图
            img = Draw.MolToImage(mol, size=(width, height))

            # 保存到文件
            # 确保目录存在 (相对于运行目录，通常是 backend/)
            save_dir = os.path.join("static", "structures")
            os.makedirs(save_dir, exist_ok=True)
            
            filename = f"{uuid.uuid4()}.png"
            file_path = os.path.join(save_dir, filename)
            
            img.save(file_path)
            
            # 返回URL
            # 假设后端服务挂载 static 目录到 /static
            # 这里的URL应该是前端可以访问的路径
            # 如果前端和后端在同一域下（通过代理），则 /static/... 是可行的
            # 如果是完全分离的，可能需要完整的URL，但通常前端会处理 base URL
            # 这里我们返回相对路径，前端显示时通常会拼上后端地址
            # 或者我们直接返回完整的 http://localhost:8000/static/... 
            # 为了通用性，我们先返回相对路径，但在 chat.py 中构建 markdown 时，
            # 如果是相对路径，markdown 图片链接在某些客户端可能无法直接解析（除非前端做了处理）
            # 考虑到这是一个 web app，浏览器会自动解析相对路径。
            
            # 为了保险起见，我们可以尝试获取 HOST 和 PORT 配置，但这比较麻烦。
            # 让我们先返回 /static/structures/{filename}
            
            image_url = f"/static/structures/{filename}"

            return {
                "success": True,
                "image": image_url,
                "smiles": Chem.MolToSmiles(mol)
            }

        except Exception as e:
            logger.error(f"生成结构图失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

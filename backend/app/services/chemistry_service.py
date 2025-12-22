from typing import Dict, Any, Optional
from rdkit import Chem
from rdkit.Chem import Descriptors, Draw, AllChem
import io
import base64
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

            # 如果不是有效的SMILES，这里暂时不支持直接从名称转换
            # 实际项目中可以集成PubChemPy或其他API来支持名称转SMILES
            # 这里简单返回None
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

            # 转为Base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            return {
                "success": True,
                "image": f"data:image/png;base64,{img_str}",
                "smiles": Chem.MolToSmiles(mol)
            }

        except Exception as e:
            logger.error(f"生成结构图失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

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
            molecule_string = molecule_string.strip()
            logger.info(f"解析分子字符串: {repr(molecule_string)}")
            
            # 抑制 RDKit 错误日志
            from rdkit import RDLogger
            lg = RDLogger.logger()
            lg.setLevel(RDLogger.CRITICAL)
            
            # 策略优化：
            # 1. 检查常用名缓存
            # 2. 尝试解析为 SMILES (如果看起来像 SMILES)
            # 3. 尝试 PubChemPy 解析名称
            # 4. 最后尝试强制解析为 SMILES (作为兜底)

            # 1. 常用名检查
            common_names = {
                "aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
                "acetylsalicylic acid": "CC(=O)OC1=CC=CC=C1C(=O)O",
                "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
                "water": "O",
                "ethanol": "CCO",
                "benzene": "c1ccccc1",
                "methane": "C",
                "ammonia": "N",
                "carbon dioxide": "O=C=O",
                "glucose": "C(C1C(C(C(C(O1)O)O)O)O)O",
                "paracetamol": "CC(=O)NC1=CC=C(O)C=C1",
                "acetaminophen": "CC(=O)NC1=CC=C(O)C=C1",
                "ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
            }

            key = molecule_string.lower()
            if key in common_names:
                logger.info(f"命中常用名缓存: {key}")
                return Chem.MolFromSmiles(common_names[key])

            # 2. 启发式检查：如果包含空格，或者长度很短且全是字母，可能是名称而不是 SMILES
            # SMILES 通常包含特殊字符 = # ( ) [ ] @ 等，或者数字
            # 但简单的 SMILES 如 C, N, O 也是字母。
            # 这里的逻辑是：如果看起来像名字，先查名字；否则先查 SMILES。
            
            is_likely_name = " " in molecule_string or (molecule_string.isalpha() and len(molecule_string) > 3)
            logger.info(f"启发式检查 is_likely_name: {is_likely_name}")
            
            if not is_likely_name:
                mol = Chem.MolFromSmiles(molecule_string)
                if mol:
                    return mol

            # 3. PubChemPy 解析
            try:
                import pubchempy as pcp
                logger.info(f"尝试使用PubChemPy解析: {molecule_string}")
                # 增加超时控制 (虽然 pcp 不直接支持，但我们可以捕获异常)
                compounds = pcp.get_compounds(molecule_string, 'name')
                if compounds:
                    smiles = compounds[0].isomeric_smiles
                    logger.info(f"PubChemPy解析成功: {molecule_string} -> {smiles}")
                    return Chem.MolFromSmiles(smiles)
            except ImportError:
                logger.warning("PubChemPy未安装，无法从名称解析分子")
            except Exception as e:
                logger.warning(f"PubChemPy解析失败 (可能是网络问题): {str(e)}")

            # 4. 如果前面都失败了，且之前没试过 SMILES (即被认为是名字但解析失败)，再试一次 SMILES
            if is_likely_name:
                 mol = Chem.MolFromSmiles(molecule_string)
                 if mol:
                     return mol

            # 恢复 RDKit 日志
            lg.setLevel(RDLogger.ERROR)

            logger.warning(f"无法解析分子字符串: {molecule_string}")
            return None

            # 恢复 RDKit 日志
            lg.setLevel(RDLogger.ERROR)

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
            mw = round(Descriptors.MolWt(mol), 4)
            logp = round(Descriptors.MolLogP(mol), 4)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            tpsa = round(Descriptors.TPSA(mol), 4)
            rotatable_bonds = Descriptors.NumRotatableBonds(mol)

            # Lipinski Rule of 5 Calculation
            lipinski_violations = 0
            if mw > 500: lipinski_violations += 1
            if logp > 5: lipinski_violations += 1
            if hbd > 5: lipinski_violations += 1
            if hba > 10: lipinski_violations += 1

            # Drug Likeness Score (Simple heuristic)
            if lipinski_violations == 0:
                drug_likeness = "High"
            elif lipinski_violations == 1:
                drug_likeness = "Moderate"
            else:
                drug_likeness = "Low"

            properties = {
                "molecular_weight": mw,
                "logp": logp,
                "h_bond_donors": hbd,
                "h_bond_acceptors": hba,
                "tpsa": tpsa,
                "num_rotatable_bonds": rotatable_bonds,
                "formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
                "lipinski_violations": lipinski_violations,
                "drug_likeness": drug_likeness
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

    async def generate_3d_structure(self, molecule_string: str) -> Dict[str, Any]:
        """生成分子3D结构数据 (SDF格式)"""
        try:
            mol = self.get_molecule_from_string(molecule_string)
            if not mol:
                return {
                    "success": False,
                    "error": "无效的SMILES或无法识别的分子"
                }

            # 添加氢原子 (3D结构必须)
            mol_3d = Chem.AddHs(mol)
            
            # 生成3D构象
            # 使用ETKDG算法生成初始构象
            params = AllChem.ETKDGv3()
            params.randomSeed = 0xf00d  # 固定种子以获得可重复结果
            res = AllChem.EmbedMolecule(mol_3d, params)
            
            if res == -1:
                # 如果生成失败，尝试更宽松的参数
                res = AllChem.EmbedMolecule(mol_3d, useRandomCoords=True)
                if res == -1:
                     return {
                        "success": False,
                        "error": "无法生成3D构象"
                    }
            
            # 能量最小化 (优化结构)
            try:
                AllChem.MMFFOptimizeMolecule(mol_3d)
            except:
                # 如果MMFF失败，尝试UFF
                AllChem.UFFOptimizeMolecule(mol_3d)

            # 转换为SDF格式字符串
            sdf_block = Chem.MolToMolBlock(mol_3d)

            return {
                "success": True,
                "sdf": sdf_block,
                "smiles": Chem.MolToSmiles(mol)
            }

        except Exception as e:
            logger.error(f"生成3D结构失败: {str(e)}")
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

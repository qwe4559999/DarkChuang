from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import asyncio
import os
from pathlib import Path
from app.core.config import settings
from loguru import logger
import re
from app.services.spectrum_service import SpectrumAnalysisService

# PaddleOCR相关导入
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logger.debug("PaddleOCR未安装，OCR功能将不可用")

class ImageService:
    """图像处理和识别服务"""
    
    def __init__(self):
        self.ocr_engine = None
        self.spectrum_service = SpectrumAnalysisService()
        self._initialize()
    
    def _initialize(self):
        """初始化图像服务"""
        try:
            logger.info("初始化图像服务...")
            
            # 初始化OCR引擎
            if PADDLEOCR_AVAILABLE:
                self.ocr_engine = PaddleOCR(
                    use_angle_cls=True,
                    lang='ch',  # 支持中英文
                    use_gpu=False,  # 根据需要调整
                    show_log=False
                )
                logger.info("PaddleOCR初始化完成")
            else:
                logger.debug("OCR引擎不可用")
            
            logger.info("图像服务初始化完成")
            
        except Exception as e:
            logger.error(f"图像服务初始化失败: {str(e)}")
            raise
    
    async def analyze_image(self, image_path: str) -> 'ImageAnalysisResult':
        """分析图像 - 使用视觉模型路线"""
        try:
            logger.info(f"开始分析图像: {image_path}")
            
            # 检查文件是否存在
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            
            # 使用视觉模型进行图像分析
            vision_analysis = await self.llm_service.analyze_general_image(image_path)
            
            # 从视觉模型分析结果中提取结构化信息
            text_content = vision_analysis.get('description', '')
            chemical_formulas = vision_analysis.get('chemical_formulas', [])
            chemical_structures = vision_analysis.get('chemical_structures', [])
            
            # 计算置信度分数
            confidence_scores = {
                'vision_model_confidence': vision_analysis.get('confidence', 0.9),
                'text_extraction_confidence': 0.95 if text_content else 0.1,
                'chemical_formula_confidence': 0.9 if chemical_formulas else 0.1,
                'overall_confidence': vision_analysis.get('confidence', 0.9)
            }
            
            # 导入这里以避免循环导入
            from app.api.image import ImageAnalysisResult
            
            result = ImageAnalysisResult(
                text_content=text_content,
                chemical_formulas=chemical_formulas,
                chemical_structures=chemical_structures,
                confidence_scores=confidence_scores,
                processing_time=0.0  # 将在调用处设置
            )
            
            logger.info(f"图像分析完成: 文本长度 {len(text_content)}, 化学公式 {len(chemical_formulas)} 个")
            return result
            
        except Exception as e:
            logger.error(f"图像分析失败: {str(e)}")
            raise
    
    async def _load_image(self, image_path: str) -> np.ndarray:
        """加载图像"""
        try:
            # 使用OpenCV加载图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法加载图像: {image_path}")
            
            # 转换为RGB格式
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            logger.debug(f"图像加载成功，尺寸: {image_rgb.shape}")
            return image_rgb
            
        except Exception as e:
            logger.error(f"加载图像失败: {str(e)}")
            raise
    
    async def _extract_text(self, image_path: str) -> str:
        """从图像中提取文本"""
        try:
            if not self.ocr_engine:
                logger.debug("OCR引擎不可用，返回空文本")
                return ""
            
            logger.debug("开始OCR文本识别")
            
            # 在线程池中执行OCR（因为PaddleOCR是同步的）
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.ocr_engine.ocr, image_path
            )
            
            # 提取文本内容
            text_lines = []
            if result and result[0]:
                for line in result[0]:
                    if len(line) >= 2:
                        text = line[1][0]  # 获取识别的文本
                        confidence = line[1][1]  # 获取置信度
                        
                        # 只保留置信度较高的文本
                        if confidence > 0.5:
                            text_lines.append(text)
            
            extracted_text = '\n'.join(text_lines)
            logger.debug(f"OCR识别完成，提取文本长度: {len(extracted_text)}")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"文本提取失败: {str(e)}")
            return ""
    
    async def _extract_chemical_formulas(self, text: str) -> List[str]:
        """从文本中提取化学公式"""
        try:
            logger.debug("开始提取化学公式")
            
            formulas = []
            
            # 化学公式的正则表达式模式
            patterns = [
                # 简单的化学公式模式（如 H2O, CO2, NaCl等）
                r'\b[A-Z][a-z]?(?:\d+)?(?:[A-Z][a-z]?(?:\d+)?)*\b',
                
                # 带括号的化学公式（如 Ca(OH)2, Al2(SO4)3等）
                r'\b[A-Z][a-z]?(?:\d+)?(?:\([A-Z][a-z]?(?:\d+)?(?:[A-Z][a-z]?(?:\d+)?)*\)(?:\d+)?)*\b',
                
                # 离子公式（如 SO4^2-, NH4+等）
                r'\b[A-Z][a-z]?(?:\d+)?(?:[A-Z][a-z]?(?:\d+)?)*[+-]?\d*\b',
                
                # 有机化学公式（如 CH3COOH, C6H12O6等）
                r'\bC(?:\d+)?H(?:\d+)?(?:O(?:\d+)?)?(?:N(?:\d+)?)?\b'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    # 验证是否为有效的化学公式
                    if self._is_valid_chemical_formula(match):
                        if match not in formulas:
                            formulas.append(match)
            
            logger.debug(f"提取到 {len(formulas)} 个化学公式")
            return formulas
            
        except Exception as e:
            logger.error(f"提取化学公式失败: {str(e)}")
            return []
    
    def _is_valid_chemical_formula(self, formula: str) -> bool:
        """验证是否为有效的化学公式"""
        try:
            # 基本验证规则
            if len(formula) < 2:
                return False
            
            # 必须以大写字母开头
            if not formula[0].isupper():
                return False
            
            # 不能全是数字
            if formula.isdigit():
                return False
            
            # 常见的化学元素符号
            common_elements = {
                'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
                'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
                'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
                'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
                'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
                'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
                'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
                'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
                'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
                'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm',
                'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds',
                'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'
            }
            
            # 检查是否包含已知的化学元素
            i = 0
            while i < len(formula):
                if formula[i].isupper():
                    # 尝试匹配两个字符的元素符号
                    if i + 1 < len(formula) and formula[i + 1].islower():
                        element = formula[i:i + 2]
                        if element in common_elements:
                            i += 2
                            continue
                    
                    # 尝试匹配单个字符的元素符号
                    element = formula[i]
                    if element in common_elements:
                        i += 1
                        continue
                    
                    # 如果不是已知元素，可能不是化学公式
                    return False
                else:
                    i += 1
            
            return True
            
        except Exception:
            return False
    
    async def _detect_chemical_structures(self, image: np.ndarray, text: str) -> List[dict]:
        """检测化学结构"""
        try:
            logger.debug("开始检测化学结构")
            
            structures = []
            
            # 这里可以实现更复杂的化学结构识别
            # 目前使用简单的基于文本的方法
            
            # 检测苯环结构
            if '苯' in text or 'benzene' in text.lower() or 'C6H6' in text:
                structures.append({
                    'type': 'benzene_ring',
                    'name': '苯环',
                    'confidence': 0.8
                })
            
            # 检测羧基
            if 'COOH' in text or '羧基' in text:
                structures.append({
                    'type': 'carboxyl_group',
                    'name': '羧基',
                    'confidence': 0.9
                })
            
            # 检测羟基
            if 'OH' in text or '羟基' in text:
                structures.append({
                    'type': 'hydroxyl_group',
                    'name': '羟基',
                    'confidence': 0.8
                })
            
            # 检测氨基
            if 'NH2' in text or '氨基' in text:
                structures.append({
                    'type': 'amino_group',
                    'name': '氨基',
                    'confidence': 0.8
                })
            
            logger.debug(f"检测到 {len(structures)} 个化学结构")
            return structures
            
        except Exception as e:
            logger.error(f"检测化学结构失败: {str(e)}")
            return []
    
    async def _calculate_confidence_scores(self, text: str, formulas: List[str], structures: List[dict]) -> dict:
        """计算置信度分数"""
        try:
            scores = {
                'text_extraction': 0.0,
                'formula_detection': 0.0,
                'structure_detection': 0.0,
                'overall': 0.0
            }
            
            # 文本提取置信度（基于文本长度和质量）
            if text:
                text_quality = min(len(text) / 100, 1.0)  # 标准化到0-1
                scores['text_extraction'] = text_quality * 0.9  # 最高0.9
            
            # 公式检测置信度
            if formulas:
                formula_score = min(len(formulas) / 5, 1.0)  # 标准化到0-1
                scores['formula_detection'] = formula_score * 0.95
            
            # 结构检测置信度
            if structures:
                structure_scores = [s.get('confidence', 0.0) for s in structures]
                avg_structure_score = sum(structure_scores) / len(structure_scores)
                scores['structure_detection'] = avg_structure_score
            
            # 总体置信度
            scores['overall'] = (
                scores['text_extraction'] * 0.4 +
                scores['formula_detection'] * 0.4 +
                scores['structure_detection'] * 0.2
            )
            
            return scores
            
        except Exception as e:
            logger.error(f"计算置信度失败: {str(e)}")
            return {
                'text_extraction': 0.0,
                'formula_detection': 0.0,
                'structure_detection': 0.0,
                'overall': 0.0
            }
    
    async def preprocess_image(self, image_path: str, output_path: str = None) -> str:
        """预处理图像以提高识别准确率"""
        try:
            logger.debug(f"开始预处理图像: {image_path}")
            
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 降噪
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # 增强对比度
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # 二值化
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 保存预处理后的图像
            if output_path is None:
                base_name = os.path.splitext(image_path)[0]
                output_path = f"{base_name}_preprocessed.png"
            
            cv2.imwrite(output_path, binary)
            
            logger.debug(f"图像预处理完成: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的图像格式"""
        return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    
    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            'ocr_available': PADDLEOCR_AVAILABLE,
            'ocr_engine': 'PaddleOCR' if PADDLEOCR_AVAILABLE else None,
            'supported_formats': self.get_supported_formats(),
            'max_image_size': settings.MAX_IMAGE_SIZE,
            'upload_dir': settings.UPLOAD_DIR
        }
    
    def calculate_confidence(self, analysis_results: Dict[str, Any]) -> float:
        """
        计算分析结果的置信度
        """
        # TODO: 实现置信度计算逻辑
        # 可以基于OCR结果的质量、检测到的化学结构数量等因素
        return 0.8  # 临时返回固定值
    
    async def analyze_spectrum_image(
        self,
        image_path: str,
        spectrum_type: str,
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析光谱图像 - 使用专门的光谱分析服务
        
        Args:
            image_path: 图像文件路径
            spectrum_type: 光谱类型 (IR, NMR, UV等)
            additional_info: 额外的上下文信息
        
        Returns:
            包含分析结果的字典
        """
        try:
            logger.info(f"开始分析{spectrum_type}光谱图像: {image_path}")
            
            # 使用专门的光谱分析服务
            result = await self.spectrum_service.analyze_spectrum(
                image_path=image_path,
                spectrum_type=spectrum_type,
                additional_info=additional_info
            )
            
            # 如果需要，可以在这里添加额外的图像处理
            if result['success']:
                # 可以添加图像预处理、质量检查等
                result['image_quality'] = await self._assess_image_quality(image_path)
            
            return result
            
        except Exception as e:
            logger.error(f"光谱图像分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'spectrum_type': spectrum_type,
                'image_path': image_path
            }
    
    async def batch_analyze_spectrum_images(
        self,
        image_paths: List[str],
        spectrum_types: List[str],
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        批量分析多个光谱图像
        
        Args:
            image_paths: 图像文件路径列表
            spectrum_types: 对应的光谱类型列表
            additional_info: 额外的上下文信息
        
        Returns:
            包含批量分析结果的字典
        """
        try:
            logger.info(f"开始批量分析{len(image_paths)}个光谱图像")
            
            result = await self.spectrum_service.batch_analyze_spectra(
                image_paths=image_paths,
                spectrum_types=spectrum_types,
                additional_info=additional_info
            )
            
            return result
            
        except Exception as e:
            logger.error(f"批量光谱图像分析失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _assess_image_quality(self, image_path: str) -> Dict[str, Any]:
        """
        评估图像质量
        
        Args:
            image_path: 图像文件路径
        
        Returns:
            包含图像质量评估结果的字典
        """
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return {'quality_score': 0.0, 'issues': ['无法读取图像']}
            
            issues = []
            quality_score = 1.0
            
            # 检查图像尺寸
            height, width = image.shape[:2]
            if width < 300 or height < 300:
                issues.append('图像分辨率较低')
                quality_score -= 0.2
            
            # 检查图像清晰度 (使用拉普拉斯算子)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:
                issues.append('图像可能模糊')
                quality_score -= 0.3
            
            # 检查亮度
            mean_brightness = np.mean(gray)
            if mean_brightness < 50:
                issues.append('图像过暗')
                quality_score -= 0.2
            elif mean_brightness > 200:
                issues.append('图像过亮')
                quality_score -= 0.2
            
            # 检查对比度
            contrast = gray.std()
            if contrast < 30:
                issues.append('图像对比度较低')
                quality_score -= 0.2
            
            quality_score = max(0.0, quality_score)
            
            return {
                'quality_score': quality_score,
                'issues': issues,
                'metrics': {
                    'width': width,
                    'height': height,
                    'sharpness': laplacian_var,
                    'brightness': mean_brightness,
                    'contrast': contrast
                }
            }
            
        except Exception as e:
            logger.error(f"图像质量评估失败: {str(e)}")
            return {
                'quality_score': 0.5,
                'issues': [f'质量评估失败: {str(e)}'],
                'metrics': {}
            }
    
    def get_supported_spectrum_types(self) -> List[str]:
        """
        获取支持的光谱类型
        
        Returns:
            支持的光谱类型列表
        """
        return self.spectrum_service.get_supported_spectrum_types()
    
    def get_supported_image_formats(self) -> List[str]:
        """
        获取支持的图像格式
        
        Returns:
            支持的图像格式列表
        """
        return self.spectrum_service.get_supported_formats()
    
    async def visualize_analysis_result(self, analysis_data: dict) -> dict:
        """
        将分析结果进行可视化格式化
        
        Args:
            analysis_data: 包含分析结果的JSON数据
        
        Returns:
            格式化后的可视化分析结果
        """
        try:
            logger.info("开始分析结果可视化处理")
            
            # 使用光谱服务的LLM来格式化结果
            visualization_result = await self.spectrum_service.format_analysis_for_visualization(analysis_data)
            
            return {
                'success': True,
                'visualization': visualization_result
            }
            
        except Exception as e:
            logger.error(f"分析结果可视化失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
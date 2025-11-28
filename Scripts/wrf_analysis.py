# import pandas as pd
# import re
# import numpy as np
#
#
# def convert_coordinate(coord_str):
#     """
#     将NXXXXXX或EXXXXXXX格式的坐标转换为十进制度
#     格式：XX°XX′XX″ 或 XXX°XX′XX″
#     """
#     if pd.isna(coord_str) or coord_str == '' or str(coord_str).strip() == '':
#         return None
#
#     coord_str = str(coord_str).strip()
#
#     # 提取数字部分
#     match = re.search(r'[NE](\d+)', coord_str)
#     if not match:
#         return None
#
#     digits = match.group(1)
#
#     try:
#         # 根据数字长度解析度分秒
#         if len(digits) == 6:  # 纬度：2位度 + 2位分 + 2位秒
#             degrees = int(digits[0:2])
#             minutes = int(digits[2:4])
#             seconds = int(digits[4:6])
#         elif len(digits) == 7:  # 经度：3位度 + 2位分 + 2位秒
#             degrees = int(digits[0:3])
#             minutes = int(digits[3:5])
#             seconds = int(digits[5:7])
#         else:
#             return None
#
#         # 转换为十进制度
#         decimal_degrees = degrees + minutes / 60 + seconds / 3600
#         return decimal_degrees
#     except:
#         return None
#
#
# def process_height(height_str):
#     """
#     处理高度列，提取m前面的数字
#     如果是xxxxm-xxxxm格式，取中间值
#     """
#     if pd.isna(height_str) or height_str == '':
#         return height_str
#
#     height_str = str(height_str)
#
#     # 检查是否包含m
#     if 'm' not in height_str:
#         # 尝试提取纯数字
#         numbers = re.findall(r'\d+', height_str)
#         if numbers:
#             return int(numbers[0])
#         return height_str
#
#     # 提取所有数字
#     numbers = re.findall(r'(\d+)m', height_str)
#
#     if not numbers:
#         # 如果没有找到带m的数字，尝试提取纯数字
#         numbers = re.findall(r'\d+', height_str)
#         if numbers:
#             return int(numbers[0])
#         return height_str
#
#     # 转换为整数
#     numbers = [int(num) for num in numbers]
#
#     # 如果只有一个数字，直接返回
#     if len(numbers) == 1:
#         return numbers[0]
#     # 如果有两个数字，取中间值
#     elif len(numbers) == 2:
#         return (numbers[0] + numbers[1]) // 2
#     else:
#         # 如果有多个数字，取平均值
#         return sum(numbers) // len(numbers)
#
#
# def complete_data_preprocessing(input_file, output_file):
#     """
#     完整的数据预处理流程
#     """
#     print("=" * 60)
#     print("开始数据预处理")
#     print("=" * 60)
#
#     # 1. 读取原始数据
#     print("\n1. 读取原始数据...")
#     try:
#         df = pd.read_excel(input_file)
#         print(f"   ✓ 成功读取文件: {input_file}")
#         print(f"   ✓ 原始数据形状: {df.shape} (行数: {df.shape[0]}, 列数: {df.shape[1]})")
#     except Exception as e:
#         print(f"   ✗ 读取文件失败: {e}")
#         return None
#
#     # 显示原始数据列名
#     print(f"\n   原始数据列名:")
#     for i, col in enumerate(df.columns):
#         print(f"     列{i}: '{col}'")
#
#     # 2. 提取需要的列
#     print("\n2. 提取需要的列...")
#     processed_data = []
#
#     for idx in range(len(df)):
#         row_data = {
#             '原始行号': idx + 1,
#             '时间': df.iloc[idx, 0] if pd.notna(df.iloc[idx, 0]) else '',  # A列
#             '原样': df.iloc[idx, 3] if pd.notna(df.iloc[idx, 3]) else '',  # D列
#             '高度原始': df.iloc[idx, 6] if pd.notna(df.iloc[idx, 6]) else '',  # G列
#             'J列原始': df.iloc[idx, 9] if pd.notna(df.iloc[idx, 9]) else '',  # J列
#             'K列原始': df.iloc[idx, 10] if pd.notna(df.iloc[idx, 10]) else ''  # K列
#         }
#
#         # 处理高度
#         row_data['高度处理'] = process_height(row_data['高度原始'])
#
#         # 转换坐标
#         row_data['纬度'] = convert_coordinate(row_data['J列原始'])
#         row_data['经度'] = convert_coordinate(row_data['K列原始'])
#
#         processed_data.append(row_data)
#
#     # 创建处理后的DataFrame
#     result_df = pd.DataFrame(processed_data)
#     print(f"   ✓ 初步处理完成，数据行数: {len(result_df)}")
#
#     # 3. 数据质量检查
#     print("\n3. 数据质量检查...")
#
#     # 检查坐标转换情况
#     j_empty = result_df['J列原始'].isna() | (result_df['J列原始'] == '')
#     k_empty = result_df['K列原始'].isna() | (result_df['K列原始'] == '')
#     lat_converted = result_df['纬度'].notna()
#     lon_converted = result_df['经度'].notna()
#
#     print(f"   J列为空的行数: {j_empty.sum()}")
#     print(f"   K列为空的行数: {k_empty.sum()}")
#     print(f"   纬度转换成功的行数: {lat_converted.sum()}")
#     print(f"   经度转换成功的行数: {lon_converted.sum()}")
#
#     # 4. 筛选有效数据
#     print("\n4. 筛选有效数据...")
#
#     # 首先筛选J列和K列都不为空的数据
#     valid_coords = result_df[(result_df['纬度'].notna()) & (result_df['经度'].notna())].copy()
#     print(f"   J列和K列都有有效坐标的数据: {len(valid_coords)} 行")
#
#     # 然后筛选在指定经纬度范围内的数据
#     lat_min, lat_max = 22.3886, 32.7584
#     lon_min, lon_max = 101.1099, 109.6137
#
#     in_range = valid_coords[
#         (valid_coords['纬度'] >= lat_min) &
#         (valid_coords['纬度'] <= lat_max) &
#         (valid_coords['经度'] >= lon_min) &
#         (valid_coords['经度'] <= lon_max)
#         ].copy()
#
#     print(f"   在指定经纬度范围内的数据: {len(in_range)} 行")
#     print(f"   经纬度范围: 纬度[{lat_min}°, {lat_max}°], 经度[{lon_min}°, {lon_max}°]")
#
#     # 5. 准备最终输出
#     print("\n5. 准备最终输出...")
#
#     # 选择最终需要的列
#     final_columns = ['时间', '原样', '高度处理', '纬度', '经度']
#     final_df = in_range[final_columns].copy()
#
#     # 重命名列
#     final_df.columns = ['时间', '原样', '高度(m)', '纬度', '经度']
#
#     # 重置索引
#     final_df = final_df.reset_index(drop=True)
#
#     # 6. 保存结果
#     print("\n6. 保存结果...")
#     try:
#         final_df.to_excel(output_file, index=False)
#         print(f"   ✓ 成功保存到: {output_file}")
#     except Exception as e:
#         print(f"   ✗ 保存文件失败: {e}")
#         return None
#
#     # 7. 生成处理报告
#     print("\n7. 生成处理报告...")
#     print("=" * 60)
#     print("数据处理报告")
#     print("=" * 60)
#     print(f"原始数据总行数: {len(df)}")
#     print(f"J列和K列都有有效坐标的数据: {len(valid_coords)}")
#     print(f"在指定经纬度范围内的数据: {len(in_range)}")
#     print(f"最终保留数据行数: {len(final_df)}")
#     print(f"数据过滤率: {(1 - len(final_df) / len(df)) * 100:.2f}%")
#
#     if len(final_df) > 0:
#         print(f"\n经纬度范围统计:")
#         print(f"  纬度范围: {final_df['纬度'].min():.6f}° - {final_df['纬度'].max():.6f}°")
#         print(f"  经度范围: {final_df['经度'].min():.6f}° - {final_df['经度'].max():.6f}°")
#         print(f"  高度范围: {final_df['高度(m)'].min()} - {final_df['高度(m)'].max()} m")
#
#     print("\n处理后的数据预览:")
#     print(final_df.head(10))
#
#     return final_df
#
#
# def debug_sample_data(input_file):
#     """
#     调试函数：显示前几行数据的详细处理过程
#     """
#     print("\n" + "=" * 60)
#     print("调试模式：详细处理过程")
#     print("=" * 60)
#
#     df = pd.read_excel(input_file)
#
#     print(f"样本数据前3行:")
#     for i in range(min(3, len(df))):
#         print(f"\n--- 第 {i + 1} 行 ---")
#         print(f"A列(时间): '{df.iloc[i, 0]}'")
#         print(f"D列(原样): '{df.iloc[i, 3]}'")
#         print(f"G列(高度): '{df.iloc[i, 6]}' -> 处理结果: {process_height(df.iloc[i, 6])}")
#         print(f"J列(纬度): '{df.iloc[i, 9]}' -> 转换结果: {convert_coordinate(df.iloc[i, 9])}")
#         print(f"K列(经度): '{df.iloc[i, 10]}' -> 转换结果: {convert_coordinate(df.iloc[i, 10])}")
#
#
# # 主程序
# if __name__ == "__main__":
#     # 配置参数
#     input_filename = "/home/Liyang/结冰报文/积冰（无缺）.xlsx"  # 请替换为您的实际文件名
#     output_filename = "/home/Liyang/结冰报文/pr_积冰（无缺）.xlsx"
#
#     print("积冰数据预处理程序")
#     print("功能说明:")
#     print("- 保留A列(时间)和D列(原样)")
#     print("- 处理G列(高度): 提取数字，处理范围值")
#     print("- 转换J列和K列坐标: NXXXXXX -> 十进制度")
#     print("- 筛选经纬度范围: N22.3886°-32.7584°, E101.1099°-109.6137°")
#     print("- 删除J列或K列为空的数据")
#
#     # 可选：运行调试模式查看样本数据处理
#     # debug_sample_data(input_filename)
#
#     # 执行完整的数据处理
#     try:
#         result = complete_data_preprocessing(input_filename, output_filename)
#         if result is not None and len(result) > 0:
#             print(f"\n✓ 数据处理完成！共处理 {len(result)} 行数据。")
#         else:
#             print(f"\n⚠ 警告: 没有符合条件的数据被保留。")
#     except FileNotFoundError:
#         print(f"\n✗ 错误: 找不到文件 '{input_filename}'，请检查文件是否存在。")
#     except Exception as e:
#         print(f"\n✗ 处理过程中出现错误: {e}")
#         import traceback
#
#         traceback.print_exc()

# 加标签
# import pandas as pd
# import re
# import numpy as np
# from datetime import datetime
# import matplotlib.pyplot as plt
# import seaborn as sns
# from collections import Counter
# import os
#
# # 设置中文字体
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
#
#
# def assign_intensity_label(text):
#     """
#     根据文本内容分配强度标签
#     优先级：强(3) > 中(2) > 轻(1) > 未知(4)
#     """
#     if pd.isna(text) or text == '':
#         return 4  # 未知
#
#     text_str = str(text)
#
#     # 检查强度关键词（按优先级排序）
#     if '强' in text_str:
#         return 3
#     elif '中' in text_str:
#         return 2
#     elif '轻' in text_str:
#         return 1
#     else:
#         return 4  # 未知
#
#
# def intensity_label_to_text(label):
#     """将数字标签转换为文本"""
#     label_map = {1: '轻', 2: '中', 3: '强', 4: '未知'}
#     return label_map.get(label, '未知')
#
#
# def analyze_icing_data_with_intensity(input_file):
#     """
#     对积冰数据进行强度标签分析和统计分析
#     """
#     print("=" * 60)
#     print("积冰数据强度分析与统计")
#     print("=" * 60)
#
#     # 读取数据
#     try:
#         df = pd.read_excel(input_file)
#         print(f"成功读取数据: {input_file}")
#         print(f"数据形状: {df.shape}")
#     except Exception as e:
#         print(f"读取文件失败: {e}")
#         return None
#
#     if len(df) == 0:
#         print("数据为空，无法进行分析")
#         return None
#
#     # 显示数据列名
#     print(f"\n数据列名: {list(df.columns)}")
#
#     # 1. 分配强度标签
#     print("\n1. 分配强度标签...")
#     df['强度标签'] = df['原样'].apply(assign_intensity_label)
#     df['强度描述'] = df['强度标签'].apply(intensity_label_to_text)
#
#     # 显示标签分布
#     label_counts = df['强度标签'].value_counts().sort_index()
#     print("强度标签分布:")
#     for label, count in label_counts.items():
#         desc = intensity_label_to_text(label)
#         print(f"  {desc}({label}): {count} 次")
#
#     # 2. 时间分析（提取月份）
#     print("\n2. 时间分析...")
#
#     # 转换时间列
#     df['时间'] = pd.to_datetime(df['时间'], errors='coerce')
#
#     # 提取年月信息
#     df['年份'] = df['时间'].dt.year
#     df['月份'] = df['时间'].dt.month
#     df['年月'] = df['时间'].dt.to_period('M')
#
#     # 显示时间范围
#     valid_times = df[df['时间'].notna()]
#     if len(valid_times) > 0:
#         print(f"时间范围: {valid_times['时间'].min()} 到 {valid_times['时间'].max()}")
#         print(f"数据覆盖月份: {valid_times['年月'].nunique()} 个月")
#
#     # 3. 月度统计分析
#     print("\n3. 月度统计分析...")
#
#     # 按年月和强度标签统计
#     monthly_stats = df.groupby(['年月', '强度标签']).size().unstack(fill_value=0)
#
#     # 添加总计列
#     monthly_stats['月度总计'] = monthly_stats.sum(axis=1)
#
#     # 重新排列列的顺序
#     intensity_columns = [1, 2, 3, 4]
#     existing_columns = [col for col in intensity_columns if col in monthly_stats.columns]
#     monthly_stats = monthly_stats[existing_columns + ['月度总计']]
#
#     # 重命名列
#     column_rename = {1: '轻', 2: '中', 3: '强', 4: '未知'}
#     monthly_stats = monthly_stats.rename(columns=column_rename)
#
#     print("月度统计详情:")
#     print(monthly_stats)
#
#     # 4. 年度统计分析
#     print("\n4. 年度统计分析...")
#     yearly_stats = df.groupby(['年份', '强度标签']).size().unstack(fill_value=0)
#     yearly_stats['年度总计'] = yearly_stats.sum(axis=1)
#
#     # 重命名列
#     yearly_stats = yearly_stats.rename(columns=column_rename)
#
#     print("年度统计详情:")
#     print(yearly_stats)
#
#     # 5. 生成详细报告
#     print("\n5. 生成详细分析报告...")
#
#     # 总体统计
#     total_records = len(df)
#     labeled_records = len(df[df['强度标签'] != 4])
#     unknown_records = len(df[df['强度标签'] == 4])
#
#     print(f"\n总体统计:")
#     print(f"总记录数: {total_records}")
#     print(f"已标记记录: {labeled_records} ({labeled_records / total_records * 100:.1f}%)")
#     print(f"未知强度记录: {unknown_records} ({unknown_records / total_records * 100:.1f}%)")
#
#     # 强度分布
#     intensity_dist = df['强度描述'].value_counts()
#     print(f"\n强度分布:")
#     for intensity, count in intensity_dist.items():
#         percentage = count / total_records * 100
#         print(f"  {intensity}: {count} 次 ({percentage:.1f}%)")
#
#     # 6. 显示带标签的样本数据
#     print(f"\n6. 带强度标签的样本数据 (前10行):")
#     sample_columns = ['时间', '原样', '强度描述', '强度标签', '高度(m)', '纬度', '经度']
#     available_columns = [col for col in sample_columns if col in df.columns]
#     print(df[available_columns].head(10))
#
#     # 7. 保存带标签的数据
#     output_file = "/home/Liyang/结冰报文/pr_积冰（label）.xlsx"  # 请替换为您希望保存的Excel文件路径
#     try:
#         df.to_excel(output_file, index=False)
#         print(f"\n✓ 带强度标签的数据已保存到: {output_file}")
#     except Exception as e:
#         print(f"保存文件失败: {e}")
#
#     return df, monthly_stats, yearly_stats
#
#
# def create_visualizations(df, monthly_stats):
#     """
#     创建数据可视化图表
#     """
#     print("\n7. 创建可视化图表...")
#
#     try:
#         # 创建图表
#         fig, axes = plt.subplots(2, 2, figsize=(15, 12))
#         fig.suptitle('积冰数据统计分析', fontsize=16)
#
#         # 1. 强度分布饼图
#         intensity_counts = df['强度描述'].value_counts()
#         axes[0, 0].pie(intensity_counts.values, labels=intensity_counts.index, autopct='%1.1f%%', startangle=90)
#         axes[0, 0].set_title('强度分布')
#
#         # 2. 月度趋势图
#         if len(monthly_stats) > 0:
#             # 准备数据
#             monthly_plot = monthly_stats.drop('月度总计',
#                                               axis=1) if '月度总计' in monthly_stats.columns else monthly_stats
#             monthly_plot.index = monthly_plot.index.astype(str)
#
#             monthly_plot.plot(kind='line', ax=axes[0, 1], marker='o')
#             axes[0, 1].set_title('月度强度趋势')
#             axes[0, 1].set_xlabel('年月')
#             axes[0, 1].set_ylabel('发生次数')
#             axes[0, 1].legend(title='强度')
#             axes[0, 1].tick_params(axis='x', rotation=45)
#
#         # 3. 高度分布箱线图（如果存在高度数据）
#         if '高度(m)' in df.columns and df['高度(m)'].notna().any():
#             height_data = pd.to_numeric(df['高度(m)'], errors='coerce').dropna()
#             if len(height_data) > 0:
#                 axes[1, 0].boxplot(height_data)
#                 axes[1, 0].set_title('高度分布箱线图')
#                 axes[1, 0].set_ylabel('高度(m)')
#
#         # 4. 经纬度散点图（如果存在经纬度数据）
#         if all(col in df.columns for col in ['纬度', '经度']):
#             valid_coords = df[(df['纬度'].notna()) & (df['经度'].notna())]
#             if len(valid_coords) > 0:
#                 scatter = axes[1, 1].scatter(valid_coords['经度'], valid_coords['纬度'],
#                                              c=valid_coords['强度标签'], cmap='viridis', alpha=0.6)
#                 axes[1, 1].set_title('积冰事件地理分布')
#                 axes[1, 1].set_xlabel('经度')
#                 axes[1, 1].set_ylabel('纬度')
#                 plt.colorbar(scatter, ax=axes[1, 1], label='强度标签')
#
#         plt.tight_layout()
#         plt.savefig('积冰数据统计分析.png', dpi=300, bbox_inches='tight')
#         print("✓ 可视化图表已保存为: 积冰数据统计分析.png")
#         plt.show()
#
#     except Exception as e:
#         print(f"创建可视化图表时出错: {e}")
#
#
# def generate_statistical_report(df, monthly_stats, yearly_stats):
#     """
#     生成详细的统计报告
#     """
#     print("\n" + "=" * 60)
#     print("详细统计报告")
#     print("=" * 60)
#
#     # 基本统计
#     total_records = len(df)
#     print(f"总记录数: {total_records}")
#
#     # 时间统计
#     if '时间' in df.columns:
#         valid_times = df[df['时间'].notna()]
#         if len(valid_times) > 0:
#             print(
#                 f"时间范围: {valid_times['时间'].min().strftime('%Y-%m-%d')} 到 {valid_times['时间'].max().strftime('%Y-%m-%d')}")
#             print(f"数据月份数: {valid_times['年月'].nunique()}")
#
#     # 强度统计
#     intensity_summary = df['强度描述'].value_counts()
#     print(f"\n强度统计:")
#     for intensity, count in intensity_summary.items():
#         percentage = count / total_records * 100
#         print(f"  {intensity}: {count} 次 ({percentage:.1f}%)")
#
#     # 月度统计摘要
#     print(f"\n月度统计摘要:")
#     print(f"统计月份数: {len(monthly_stats)}")
#     if len(monthly_stats) > 0:
#         avg_monthly = monthly_stats.mean()
#         print("月平均值:")
#         for col in avg_monthly.index:
#             print(f"  {col}: {avg_monthly[col]:.1f}")
#
#     # 年度统计摘要
#     if '年份' in df.columns:
#         yearly_summary = df['年份'].value_counts().sort_index()
#         print(f"\n年度记录分布:")
#         for year, count in yearly_summary.items():
#             print(f"  {year}: {count} 次")
#
#
# # 主程序
# if __name__ == "__main__":
#     # 输入文件路径
#     input_file = "/home/Liyang/结冰报文/pr_积冰（无缺）.xlsx"  # 请替换为您的实际文件路径
#
#     print("积冰数据强度分析与统计程序")
#     print("功能说明:")
#     print("- 自动识别强度标签: 强(3), 中(2), 轻(1), 未知(4)")
#     print("- 生成月度统计分析")
#     print("- 生成年度统计分析")
#     print("- 创建可视化图表")
#     print("- 输出带标签的完整数据集")
#
#     try:
#         # 执行分析
#         result_df, monthly_stats, yearly_stats = analyze_icing_data_with_intensity(input_file)
#
#         if result_df is not None:
#             # 创建可视化
#             create_visualizations(result_df, monthly_stats)
#
#             # 生成详细报告
#             generate_statistical_report(result_df, monthly_stats, yearly_stats)
#
#             print(f"\n✓ 分析完成！")
#             print(f"✓ 带标签的数据已保存")
#             print(f"✓ 统计图表已生成")
#         else:
#             print("分析失败，请检查输入文件")
#
#     except Exception as e:
#         print(f"程序执行过程中出现错误: {e}")
#         import traceback
#
#         traceback.print_exc()

# 可视化
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 定义强度映射
intensity_map = {1: '轻', 2: '中', 3: '强', 4: '未知'}

# 创建自定义颜色方案
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
intensity_colors = ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3']  # 轻、中、强、未知
season_colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFD700']  # 春、夏、秋、冬


def create_advanced_visualizations(df):
    """
    为带标签数据创建高级可视化分析
    """
    print("=" * 80)
    print("带标签积冰数据高级可视化分析")
    print("=" * 80)

    # 数据预处理
    df['时间'] = pd.to_datetime(df['时间'])
    df['年份'] = df['时间'].dt.year
    df['月份'] = df['时间'].dt.month
    df['季节'] = df['时间'].dt.month.map({12: '冬', 1: '冬', 2: '冬',
                                          3: '春', 4: '春', 5: '春',
                                          6: '夏', 7: '夏', 8: '夏',
                                          9: '秋', 10: '秋', 11: '秋'})
    df['星期'] = df['时间'].dt.day_name()
    df['小时'] = df['时间'].dt.hour

    # 强度描述映射
    df['强度描述'] = df['强度标签'].map(intensity_map)

    # 创建第一个大画布 - 核心分析
    fig1 = plt.figure(figsize=(20, 16))
    fig1.suptitle('积冰数据核心统计分析', fontsize=20, fontweight='bold', y=0.95)

    # 使用GridSpec创建复杂的布局
    gs = gridspec.GridSpec(4, 4, figure=fig1)

    # 1. 强度分布旭日图 (左上)
    ax1 = fig1.add_subplot(gs[0, 0:2])
    create_sunburst_chart(df, ax1)

    # 2. 时空分布热力图 (右上)
    ax2 = fig1.add_subplot(gs[0, 2:4])
    create_spatiotemporal_heatmap(df, ax2)

    # 3. 高度-强度关系小提琴图 (中上左)
    ax3 = fig1.add_subplot(gs[1, 0])
    create_height_intensity_violin(df, ax3)

    # 4. 月度趋势面积图 (中上右)
    ax4 = fig1.add_subplot(gs[1, 1])
    create_monthly_trend_area(df, ax4)

    # 5. 地理分布气泡图 (中下左)
    ax5 = fig1.add_subplot(gs[1, 2])
    create_geographic_bubble(df, ax5)

    # 6. 24小时分布极坐标图 (中下右)
    ax6 = fig1.add_subplot(gs[1, 3], polar=True)
    create_hourly_polar(df, ax6)

    # 7. 季节性堆叠面积图 (下左)
    ax7 = fig1.add_subplot(gs[2, 0:2])
    create_seasonal_stacked(df, ax7)

    # 8. 高度分布雷达图 (下右)
    ax8 = fig1.add_subplot(gs[2, 2:4], polar=True)
    create_height_radar(df, ax8)

    # 9. 强度时间序列热力图 (底部左)
    ax9 = fig1.add_subplot(gs[3, 0:2])
    create_intensity_timeline_heatmap(df, ax9)

    # 10. 多变量关系热力图 (底部右)
    ax10 = fig1.add_subplot(gs[3, 2:4])
    create_multivariate_heatmap(df, ax10)

    plt.tight_layout()
    plt.show()

    # 创建第二个画布 - 深度分析
    create_deep_analysis(df)

    print("✓ 所有高级可视化图表已创建完成")


def create_sunburst_chart(df, ax):
    """创建强度分布旭日图"""
    intensity_counts = df['强度描述'].value_counts()

    # 创建旭日图数据
    sizes = intensity_counts.values
    labels = [f'{label}\n{count}' for label, count in zip(intensity_counts.index, sizes)]
    colors = intensity_colors[:len(sizes)]

    # 绘制旭日图
    wedges, texts = ax.pie(sizes, labels=labels, colors=colors, startangle=90,
                           wedgeprops=dict(width=0.5, edgecolor='w', linewidth=2))

    # 美化文本
    for text in texts:
        text.set_fontweight('bold')
        text.set_fontsize(10)

    ax.set_title('强度分布旭日图', fontsize=14, fontweight='bold', pad=20)
    ax.set_aspect('equal')


def create_spatiotemporal_heatmap(df, ax):
    """创建时空分布热力图"""
    # 创建月份-小时热力图
    heatmap_data = df.groupby(['月份', '小时']).size().unstack(fill_value=0)

    # 使用seaborn热力图
    sns.heatmap(heatmap_data, cmap='YlOrRd', ax=ax, cbar_kws={'label': '发生次数'},
                linewidths=0.5, linecolor='white')

    ax.set_title('时空分布热力图\n(月份 vs 小时)', fontsize=14, fontweight='bold')
    ax.set_xlabel('小时')
    ax.set_ylabel('月份')


def create_height_intensity_violin(df, ax):
    """创建高度-强度关系小提琴图"""
    if '高度(m)' in df.columns:
        # 按强度分组
        data_by_intensity = []
        labels = []
        for intensity in [1, 2, 3, 4]:
            if intensity in df['强度标签'].values:
                heights = pd.to_numeric(df[df['强度标签'] == intensity]['高度(m)'], errors='coerce').dropna()
                if len(heights) > 0:
                    data_by_intensity.append(heights)
                    labels.append(intensity_map.get(intensity))

        if data_by_intensity:
            # 创建小提琴图
            violin_parts = ax.violinplot(data_by_intensity, showmeans=True, showmedians=True, showextrema=True)

            # 设置颜色
            for pc, color in zip(violin_parts['bodies'], intensity_colors[:len(data_by_intensity)]):
                pc.set_facecolor(color)
                pc.set_alpha(0.8)
                pc.set_edgecolor('black')

            # 设置其他元素的颜色
            violin_parts['cmeans'].set_color('red')
            violin_parts['cmedians'].set_color('blue')
            violin_parts['cmins'].set_color('black')
            violin_parts['cmaxes'].set_color('black')
            violin_parts['cbars'].set_color('black')

            ax.set_xticks(range(1, len(labels) + 1))
            ax.set_xticklabels(labels)
            ax.set_ylabel('高度 (m)')
            ax.set_title('高度-强度关系小提琴图', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)


def create_monthly_trend_area(df, ax):
    """创建月度趋势面积图"""
    # 按月份和强度统计
    monthly_data = df.groupby(['月份', '强度标签']).size().unstack(fill_value=0)
    monthly_data = monthly_data.reindex(range(1, 13), fill_value=0)

    # 重命名列
    monthly_data = monthly_data.rename(columns=intensity_map)

    # 绘制堆叠面积图
    monthly_data.plot.area(ax=ax, color=intensity_colors, alpha=0.8, linewidth=2)

    ax.set_title('月度强度趋势面积图', fontsize=14, fontweight='bold')
    ax.set_xlabel('月份')
    ax.set_ylabel('发生次数')
    ax.legend(title='强度', loc='upper right')
    ax.grid(True, alpha=0.3)


def create_geographic_bubble(df, ax):
    """创建地理分布气泡图"""
    if all(col in df.columns for col in ['纬度', '经度']):
        valid_coords = df[df['纬度'].notna() & df['经度'].notna()].copy()
        if len(valid_coords) > 0:
            # 按位置分组计数
            geo_counts = valid_coords.groupby(['纬度', '经度']).size().reset_index(name='count')

            # 创建气泡图，气泡大小表示频次，颜色表示平均强度
            scatter = ax.scatter(geo_counts['经度'], geo_counts['纬度'],
                                 s=geo_counts['count'] * 10,  # 气泡大小
                                 c=geo_counts['count'],  # 气泡颜色
                                 cmap='viridis', alpha=0.7,
                                 edgecolors='white', linewidth=0.5)

            ax.set_title('地理分布气泡图', fontsize=14, fontweight='bold')
            ax.set_xlabel('经度')
            ax.set_ylabel('纬度')
            plt.colorbar(scatter, ax=ax, label='发生频次')
            ax.grid(True, alpha=0.3)


def create_hourly_polar(df, ax):
    """创建24小时分布极坐标图"""
    hourly_data = df['小时'].value_counts().sort_index()
    hourly_data = hourly_data.reindex(range(24), fill_value=0)

    # 创建极坐标图
    angles = np.linspace(0, 2 * np.pi, 24, endpoint=False).tolist()
    values = hourly_data.values.tolist()
    values += values[:1]  # 闭合图形
    angles += angles[:1]  # 闭合图形

    ax.plot(angles, values, 'o-', linewidth=3, color='#FF6B6B', markersize=8)
    ax.fill(angles, values, alpha=0.3, color='#FF6B6B')

    # 设置极坐标参数
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([f'{i:02d}' for i in range(24)])
    ax.set_title('24小时分布极坐标图', fontsize=14, fontweight='bold', pad=20)
    ax.grid(True)


def create_seasonal_stacked(df, ax):
    """创建季节性堆叠面积图"""
    seasonal_data = df.groupby(['季节', '强度描述']).size().unstack(fill_value=0)

    # 确保季节顺序正确
    season_order = ['春', '夏', '秋', '冬']
    seasonal_data = seasonal_data.reindex(season_order)

    # 绘制堆叠柱状图
    seasonal_data.plot(kind='bar', stacked=True, ax=ax,
                       color=intensity_colors, alpha=0.8, edgecolor='black')

    ax.set_title('季节性强度分布', fontsize=14, fontweight='bold')
    ax.set_xlabel('季节')
    ax.set_ylabel('发生次数')
    ax.legend(title='强度', loc='upper right')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=0)


def create_height_radar(df, ax):
    """创建高度分布雷达图"""
    if '高度(m)' in df.columns:
        height_data = pd.to_numeric(df['高度(m)'], errors='coerce').dropna()
        if len(height_data) > 0:
            # 创建高度区间
            height_bins = [0, 2000, 4000, 6000, 8000, 10000, float('inf')]
            height_labels = ['<2km', '2-4km', '4-6km', '6-8km', '8-10km', '>10km']
            height_categories = pd.cut(height_data, bins=height_bins, labels=height_labels)
            height_dist = height_categories.value_counts().sort_index()

            # 创建雷达图数据
            angles = np.linspace(0, 2 * np.pi, len(height_dist), endpoint=False).tolist()
            values = height_dist.values.tolist()
            values += values[:1]  # 闭合图形
            angles += angles[:1]  # 闭合图形

            ax.plot(angles, values, 'o-', linewidth=2, color='#4ECDC4', markersize=6)
            ax.fill(angles, values, alpha=0.3, color='#4ECDC4')

            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(height_dist.index)
            ax.set_title('高度分布雷达图', fontsize=14, fontweight='bold', pad=20)
            ax.grid(True)


def create_intensity_timeline_heatmap(df, ax):
    """创建强度时间序列热力图"""
    # 按日期和强度统计
    df['日期'] = df['时间'].dt.date
    timeline_data = df.groupby(['日期', '强度描述']).size().unstack(fill_value=0)

    # 如果数据量太大，可以按周或月聚合
    if len(timeline_data) > 60:  # 如果超过60天，按周聚合
        df['周'] = df['时间'].dt.to_period('W')
        timeline_data = df.groupby(['周', '强度描述']).size().unstack(fill_value=0)
        timeline_data.index = timeline_data.index.astype(str)

    # 绘制热力图
    sns.heatmap(timeline_data.T, cmap='YlOrRd', ax=ax, cbar_kws={'label': '发生次数'})
    ax.set_title('强度时间序列热力图', fontsize=14, fontweight='bold')
    ax.set_xlabel('时间')
    ax.set_ylabel('强度')


def create_multivariate_heatmap(df, ax):
    """创建多变量关系热力图"""
    # 创建月份-强度-高度的关系热力图
    if '高度(m)' in df.columns:
        # 将高度分箱
        df['高度类别'] = pd.cut(pd.to_numeric(df['高度(m)'], errors='coerce'),
                                bins=5, labels=['很低', '低', '中', '高', '很高'])

        # 创建月份-强度-高度的三维关系数据
        multivariate_data = df.groupby(['月份', '强度描述', '高度类别']).size().unstack(fill_value=0)

        # 绘制热力图
        sns.heatmap(multivariate_data, cmap='YlOrRd', ax=ax, cbar_kws={'label': '发生次数'})
        ax.set_title('多变量关系热力图\n(月份-强度-高度)', fontsize=14, fontweight='bold')
        ax.set_xlabel('高度类别')
        ax.set_ylabel('月份-强度')


def create_deep_analysis(df):
    """创建深度分析图表"""
    fig2 = plt.figure(figsize=(18, 12))
    fig2.suptitle('积冰数据深度分析', fontsize=20, fontweight='bold', y=0.95)

    # 使用GridSpec创建复杂布局
    gs2 = gridspec.GridSpec(3, 3, figure=fig2)

    # 1. 强度-高度联合分布图 (左上)
    ax1 = fig2.add_subplot(gs2[0, 0])
    create_joint_distribution(df, ax1)

    # 2. 时间序列分解图 (中上)
    ax2 = fig2.add_subplot(gs2[0, 1])
    create_time_series_decomposition(df, ax2)

    # 3. 地理密度等高线图 (右上)
    ax3 = fig2.add_subplot(gs2[0, 2])
    create_geographic_contour(df, ax3)

    # 4. 强度转移矩阵热力图 (中左)
    ax4 = fig2.add_subplot(gs2[1, 0])
    create_intensity_transition_heatmap(df, ax4)

    # 5. 多变量平行坐标图 (中)
    ax5 = fig2.add_subplot(gs2[1, 1])
    create_parallel_coordinates(df, ax5)

    # 6. 强度持续时间分布 (中右)
    ax6 = fig2.add_subplot(gs2[1, 2])
    create_duration_distribution(df, ax6)

    # 7. 高度分布小提琴-箱线组合图 (下左)
    ax7 = fig2.add_subplot(gs2[2, 0])
    create_violin_box_combo(df, ax7)

    # 8. 时空立方体投影图 (下中)
    ax8 = fig2.add_subplot(gs2[2, 1])
    create_spatial_temporal_projection(df, ax8)

    # 9. 强度模式桑基图 (下右)
    ax9 = fig2.add_subplot(gs2[2, 2])
    create_sankey_diagram(df, ax9)

    plt.tight_layout()
    plt.show()


def create_joint_distribution(df, ax):
    """创建强度-高度联合分布图"""
    if '高度(m)' in df.columns:
        valid_data = df[df['高度(m)'].notna()].copy()
        valid_data['高度(m)'] = pd.to_numeric(valid_data['高度(m)'], errors='coerce')
        valid_data = valid_data.dropna(subset=['高度(m)'])

        if len(valid_data) > 0:
            # 使用hexbin显示联合分布
            hb = ax.hexbin(valid_data['强度标签'], valid_data['高度(m)'],
                           gridsize=20, cmap='YlOrRd', alpha=0.8)

            ax.set_xlabel('强度标签')
            ax.set_ylabel('高度 (m)')
            ax.set_title('强度-高度联合分布', fontsize=12, fontweight='bold')
            plt.colorbar(hb, ax=ax, label='频次密度')


def create_time_series_decomposition(df, ax):
    """创建时间序列分解图"""
    # 按日期统计总次数
    daily_counts = df.groupby(df['时间'].dt.date).size()

    # 绘制时间序列
    ax.plot(daily_counts.index, daily_counts.values, color='#FF6B6B', linewidth=2)

    # 添加移动平均线
    if len(daily_counts) > 7:
        moving_avg = daily_counts.rolling(window=7).mean()
        ax.plot(daily_counts.index, moving_avg.values, color='#4ECDC4', linewidth=2, linestyle='--',
                label='7日移动平均')
        ax.legend()

    ax.set_title('时间序列分解', fontsize=12, fontweight='bold')
    ax.set_xlabel('日期')
    ax.set_ylabel('每日发生次数')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)


def create_geographic_contour(df, ax):
    """创建地理密度等高线图"""
    if all(col in df.columns for col in ['纬度', '经度']):
        valid_coords = df[df['纬度'].notna() & df['经度'].notna()]
        if len(valid_coords) > 0:
            # 创建密度等高线图
            sns.kdeplot(x=valid_coords['经度'], y=valid_coords['纬度'],
                        cmap='Reds', fill=True, alpha=0.7, ax=ax)

            ax.set_title('地理密度等高线图', fontsize=12, fontweight='bold')
            ax.set_xlabel('经度')
            ax.set_ylabel('纬度')
            ax.grid(True, alpha=0.3)


def create_intensity_transition_heatmap(df, ax):
    """创建强度转移矩阵热力图（简化版）"""
    # 这里简化实现，实际应用中需要有时间序列的强度转移数据
    intensity_counts = df['强度描述'].value_counts()
    ax.bar(intensity_counts.index, intensity_counts.values, color=intensity_colors[:len(intensity_counts)])
    ax.set_title('强度分布柱状图', fontsize=12, fontweight='bold')
    ax.set_ylabel('发生次数')
    plt.xticks(rotation=45)


def create_parallel_coordinates(df, ax):
    """创建多变量平行坐标图（简化版）"""
    # 这里简化实现，选择几个关键变量
    if '高度(m)' in df.columns:
        sample_data = df[['强度标签', '月份', '小时']].copy()
        sample_data['高度类别'] = pd.cut(pd.to_numeric(df['高度(m)'], errors='coerce'),
                                         bins=5, labels=['很低', '低', '中', '高', '很高'])
        sample_data = sample_data.dropna()

        # 使用平行坐标图显示多变量关系
        parallel_data = sample_data.groupby(['强度标签', '高度类别']).size().unstack(fill_value=0)
        sns.heatmap(parallel_data, cmap='YlOrRd', ax=ax)
        ax.set_title('多变量关系热力图', fontsize=12, fontweight='bold')


def create_duration_distribution(df, ax):
    """创建强度持续时间分布（简化版）"""
    # 这里简化实现，显示各强度的持续时间分布
    intensity_duration = df.groupby('强度描述').size()
    ax.pie(intensity_duration.values, labels=intensity_duration.index,
           autopct='%1.1f%%', colors=intensity_colors[:len(intensity_duration)])
    ax.set_title('强度占比饼图', fontsize=12, fontweight='bold')


def create_violin_box_combo(df, ax):
    """创建高度分布小提琴-箱线组合图"""
    if '高度(m)' in df.columns:
        height_data = pd.to_numeric(df['高度(m)'], errors='coerce').dropna()
        if len(height_data) > 0:
            # 创建组合图
            sns.violinplot(y=height_data, ax=ax, color='lightblue', inner='box')
            ax.set_title('高度分布小提琴-箱线组合图', fontsize=12, fontweight='bold')
            ax.set_ylabel('高度 (m)')


def create_spatial_temporal_projection(df, ax):
    """创建时空立方体投影图（简化版）"""
    # 这里简化实现，显示月份和小时的二维投影
    projection_data = df.groupby(['月份', '小时']).size().unstack(fill_value=0)
    ax.imshow(projection_data.values, cmap='YlOrRd', aspect='auto', interpolation='nearest')
    ax.set_title('时空投影图', fontsize=12, fontweight='bold')
    ax.set_xlabel('小时')
    ax.set_ylabel('月份')


def create_sankey_diagram(df, ax):
    """创建强度模式桑基图（简化版）"""
    # 这里简化实现，显示强度与季节的关系
    season_intensity = df.groupby(['季节', '强度描述']).size().unstack(fill_value=0)
    season_intensity.plot(kind='bar', stacked=True, ax=ax, color=intensity_colors)
    ax.set_title('季节-强度关系图', fontsize=12, fontweight='bold')
    ax.set_xlabel('季节')
    ax.set_ylabel('发生次数')
    plt.xticks(rotation=0)


# 主程序
if __name__ == "__main__":
    # 输入文件路径 - 带标签的数据
    input_file = "/home/Liyang/结冰报文/pr_积冰（label）.xlsx"  # 请替换为您的带标签数据文件路径

    print("带标签积冰数据高级可视化分析程序")
    print("功能说明:")
    print("- 针对时间、高度(m)、纬度、经度、强度标签五列数据进行深度分析")
    print("- 创建多种高级可视化图表")
    print("- 提供全面且美观的统计分析")

    try:
        # 读取带标签的数据
        df = pd.read_excel(input_file)
        print(f"成功读取带标签数据: {input_file}")
        print(f"数据形状: {df.shape}")
        print(f"数据列: {list(df.columns)}")

        # 确保只有五列数据
        required_columns = ['时间', '高度(m)', '纬度', '经度', '强度标签']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"错误：缺少必要的列: {missing_columns}")
        else:
            # 只保留需要的五列
            df = df[required_columns].copy()
            print(f"处理后数据形状: {df.shape}")

            # 创建高级可视化分析
            create_advanced_visualizations(df)

            print(f"\n🎉 高级可视化分析完成！")
            print(f"✓ 所有统计分析图表已显示")

    except Exception as e:
        print(f"程序执行过程中出现错误: {e}")
        import traceback

        traceback.print_exc()
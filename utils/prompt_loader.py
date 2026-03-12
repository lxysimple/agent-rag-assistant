from utils.config_handler import prompts_config
from utils.path_tool import get_abs_path
from utils.logger_handler import logger

def load_system_prompts() -> str:
    """
    加载系统提示词（主提示词）内容。
    对应配置中的 `main_prompt_path`，通常用于智能体的系统级提示词。
    """
    try:
        system_prompt_path = get_abs_path(prompts_config["main_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts] 在 yaml 配置项中没有 main_promptpath 配置项")
        raise e
    
    try:
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompts] 解析系统提示词出错, {str(e)}")
        raise e


def load_rag_prompts():
    """ 
    加载 RAG 相关提示词内容。
    对应配置中的 `rag_summarize_prompt_path`，通常用于 RAG 检索后的总结与回答生成
    """
    try:
        rag_prompt_path = get_abs_path(prompts_config["rag_summarize_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_rag_prompts] 在 yaml 配置项中没有 rag_summarize_prompt_path 配置项")
        raise e
    
    try:
        return open(rag_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_prompts] 解析 RAG 提示词出错, {str(e)}")
        raise e
    

def load_report_prompts():
    """
    加载报告生成相关提示词内容。
    对应配置中的 `report_prompt_path`，通常用于生成用户使用报告与优化建议。
    """
    try:
        report_prompt_path = get_abs_path(prompts_config["report_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_report_prompts] 在 yaml 配置项中没有 report_prompt_path 配置项")
        raise e
    
    try:
        return open(report_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_report_prompts] 解析系统提示词出错, {str(e)}")
        raise e


# if __name__ == "__main__":
    # print(load_system_prompts())
    # print(load_rag_prompts())
    # print(load_report_prompts())








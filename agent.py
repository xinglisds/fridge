import os
import json
import openai
from typing import List, Dict, Any, Optional, Callable
from PIL import Image

# 导入集中管理的API密钥
from config import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

class FridgeChefAgent:
    """
    Agent architecture for FridgeChef AI using GPT function calling capabilities.
    Handles routing between different tools and functions.
    """
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.tools = {}
        self.conversation_history = []
        self.register_default_tools()
    
    def register_tool(self, name: str, function: Callable, description: str) -> None:
        """Register a tool that the agent can use"""
        self.tools[name] = {
            "function": function,
            "description": description
        }
    
    def register_default_tools(self) -> None:
        """Register the default set of tools"""
        # Import here to avoid circular imports
        from food_recognition import recognize_food_with_gpt_vision
        from recipe_generation import generate_recipes_with_gpt
        
        # Register food recognition tool
        self.register_tool(
            "recognize_ingredients",
            recognize_food_with_gpt_vision,
            "Recognize food ingredients from an image"
        )
        
        # Register recipe generation tool
        self.register_tool(
            "generate_recipes",
            generate_recipes_with_gpt,
            "Generate recipes based on available ingredients"
        )
    
    def create_tool_specifications(self) -> List[Dict[str, Any]]:
        """Create tool specifications for GPT function calling"""
        tool_specs = []
        
        # Recognize ingredients tool
        tool_specs.append({
            "type": "function",
            "function": {
                "name": "recognize_ingredients",
                "description": "Analyze an image to identify food ingredients",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_description": {
                            "type": "string",
                            "description": "Description of the image contents"
                        }
                    },
                    "required": ["image_description"]
                }
            }
        })
        
        # Generate recipes tool
        tool_specs.append({
            "type": "function",
            "function": {
                "name": "generate_recipes",
                "description": "Generate recipe recommendations based on ingredients",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ingredients": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of available ingredients"
                        },
                        "dietary_restrictions": {
                            "type": "string",
                            "description": "Any dietary restrictions to consider (optional)"
                        }
                    },
                    "required": ["ingredients"]
                }
            }
        })
        
        return tool_specs
    
    def process_image(self, image: Image.Image) -> List[str]:
        """Process an image to identify ingredients"""
        if "recognize_ingredients" in self.tools:
            return self.tools["recognize_ingredients"]["function"](image, self.language)
        return []
    
    def generate_recipes(self, ingredients: List[str], dietary_restrictions: Optional[str] = None) -> List[Dict]:
        """Generate recipes based on ingredients"""
        if "generate_recipes" in self.tools:
            return self.tools["generate_recipes"]["function"](ingredients, self.language, dietary_restrictions)
        return []
    
    def run_agent(self, query: str, image: Optional[Image.Image] = None) -> Dict[str, Any]:
        """
        Run the agent with a user query and optional image
        Returns the agent's response
        """
        # Add user query to conversation history
        self.conversation_history.append({"role": "user", "content": query})
        
        # Prepare messages for GPT
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
        ] + self.conversation_history
        
        # Add image to the latest user message if provided
        if image and messages[-1]["role"] == "user":
            # Process the image directly
            ingredients = self.process_image(image)
            result = {
                "action": "ingredient_recognition",
                "ingredients": ingredients
            }
            return result
        
        # For recipe generation, extract ingredients from the query
        if "recipe" in query.lower() or "cook" in query.lower():
            # Extract ingredients from the query or context
            ingredients = self._extract_ingredients_from_context()
            if ingredients:
                recipes = self.generate_recipes(ingredients)
                result = {
                    "action": "recipe_generation",
                    "recipes": recipes
                }
                return result
        
        # If we reach here, use standard GPT chat completion
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                tools=self.create_tool_specifications(),
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # 保存消息到对话历史，确保使用正确的格式
            assistant_message = {
                "role": "assistant", 
                "content": response_message.get("content", "")
            }
            self.conversation_history.append(assistant_message)
            
            # 更新处理tool_calls的方式
            if "tool_calls" in response_message:
                result = self._handle_tool_calls(response_message["tool_calls"])
                return result
            else:
                # Standard text response
                return {
                    "action": "text_response",
                    "content": response_message.get("content", "")
                }
                
        except Exception as e:
            print(f"Error running agent: {str(e)}")
            return {
                "action": "error",
                "error": str(e)
            }
    
    def _handle_tool_calls(self, tool_calls):
        """Handle tool calls from GPT"""
        for tool_call in tool_calls:
            # 适应不同格式的tool_calls
            if isinstance(tool_call, dict):
                # 如果是字典格式
                function_name = tool_call.get("function", {}).get("name", "")
                function_args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
            else:
                # 如果是对象格式
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "recognize_ingredients":
                # This would be handled differently in production
                # For now, return a placeholder
                return {
                    "action": "ingredient_recognition",
                    "message": "Image processing would happen here"
                }
            
            elif function_name == "generate_recipes":
                ingredients = function_args.get("ingredients", [])
                dietary_restrictions = function_args.get("dietary_restrictions")
                recipes = self.generate_recipes(ingredients, dietary_restrictions)
                return {
                    "action": "recipe_generation",
                    "recipes": recipes
                }
        
        return {"action": "unknown_tool"}
    
    def _extract_ingredients_from_context(self) -> List[str]:
        """Extract ingredients from conversation context"""
        # In a real implementation, this would analyze the conversation history
        # For now, return an empty list and let the caller provide ingredients
        return []
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt based on language"""
        if self.language == "zh":
            return """你是FridgeChef AI小厨，一个食谱推荐助手。用户会上传冰箱的照片，你需要识别其中的食材，并根据这些食材提供美味的家常菜谱。请保持友好和有帮助的态度。"""
        else:
            return """You are FridgeChef AI, a recipe recommendation assistant. Users will upload photos of their refrigerator, and you need to identify the ingredients and provide delicious home-style recipes based on these ingredients. Please maintain a friendly and helpful attitude.""" 
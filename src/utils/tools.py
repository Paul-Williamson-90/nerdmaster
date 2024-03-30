from typing import Callable
from langchain.tools import StructuredTool
from langchain.pydantic_v1 import Field, create_model

def create_tool(callable:Callable):
    method = callable
    args = {k:v for k,v in method.__annotations__.items() if k != "self" and k != "return"}
    name = method.__name__
    doc = method.__doc__
    func_desc = doc[doc.find("<desc>") + len("<desc>"):doc.find("</desc>")]
    arg_desc = dict()
    for arg in args.keys():
        desc = doc[doc.find(f"<{arg}>: ")+len(f"<{arg}>: "):]
        desc = desc[:desc.find("\n")]
        arg_desc[arg] = desc
    arg_fields = dict()
    for k,v in args.items():
        arg_fields[k] = (v, Field(description=arg_desc[k]))

    # Create the new model
    Model = create_model('Model', **arg_fields)

    tool = StructuredTool.from_function(
        func=method,
        name=name,
        description=func_desc,
        args_schema=Model,
        return_direct=False,
    )
    return tool

def create_action_tool(callable:Callable, name: str):
    method = callable
    args = {k:v for k,v in method.__annotations__.items() if k != "self" and k != "return"}
    doc = method.__doc__
    func_desc = doc[doc.find("<desc>") + len("<desc>"):doc.find("</desc>")]
    arg_desc = dict()
    for arg in args.keys():
        desc = doc[doc.find(f"<{arg}>: ")+len(f"<{arg}>: "):]
        desc = desc[:desc.find("\n")]
        arg_desc[arg] = desc
    arg_fields = dict()
    for k,v in args.items():
        arg_fields[k] = (v, Field(description=arg_desc[k]))

    # Create the new model
    Model = create_model('Model', **arg_fields)

    tool = StructuredTool.from_function(
        func=method,
        name=name,
        description=func_desc,
        args_schema=Model,
        return_direct=False,
    )
    return tool
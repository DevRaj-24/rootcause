from enum import Enum
from typing import Dict,List,Optional
from pydantic import BaseModel,Field
class BaseDeeplink(BaseModel): deeplink:str
class Deeplink(BaseDeeplink):
 description:str
 message:Optional[str]=""
 classes:Optional[Dict[str,str]]=None
 originalType:Optional[str]=None
class Condition(str,Enum): greater="greater"; equal="equal"; less="less"
class ResultTypes(str,Enum): boolean="boolean"; intNum="integer"; string="str"; floatNum="float"
class ActionCategory(str,Enum): auto="auto"; manual="manual"; critical="critical"
class ValidationDeepLink(BaseDeeplink):
 key:str
 resultType:Optional[ResultTypes]=None
 condition:Optional[Condition]=None
 value:Optional[str]=None
class StepGroup(BaseModel):
 steps:List[str]
 validationDeeplink:Optional[ValidationDeepLink]=None
 actionableDeeplink:Optional[Deeplink]=None
class Action(BaseModel):
 actionName:str
 description:str
 stepGroups:List[StepGroup]
 category:Optional[ActionCategory]=ActionCategory.manual
class Goal(BaseModel):
 goal:str
 title:str
 actions:List[Action]
 score:float
class ResponseBody(BaseModel): contexts:List[Goal]=Field(default_factory=list)
class TroubleshootRequest(BaseModel):
 query:str=Field(min_length=3)
 siis_response:Optional[str]=None
class TroubleshootResponse(BaseModel):
 query:str
 response:ResponseBody
 query_variations:List[str]=Field(default_factory=list)
 meta:Dict[str,object]=Field(default_factory=dict)

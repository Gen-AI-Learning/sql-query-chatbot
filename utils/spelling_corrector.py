from typing import Dict, List, Union

class EnhancedSpellingCorrector:
    _instance = None 
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Create the instance and store it in the class variable
            cls._instance = super(EnhancedSpellingCorrector, cls).__new__(cls)
        return cls._instance

    def __init__(self, schema_info: Dict[str, Dict[str, Union[List[str], Dict[str, List[str]]]]]):
        self.schema_info = schema_info

    def correct_spelling(self, query: str) -> str:
        words = query.split()
        corrected_words = []

        for word in words:
            corrected = word
            for table, info in self.schema_info.items():
                # Check table name
                if table.lower().startswith(word.lower()):
                    corrected = table
                    break
                
                # Check column names
                for column, values in info.items():
                    if column.lower().startswith(word.lower()):
                        corrected = column
                        break
                    
                    # Check predefined values if they exist
                    if isinstance(values, list) and any(value.lower().startswith(word.lower()) for value in values):
                        corrected = next(value for value in values if value.lower().startswith(word.lower()))
                        break
                
                if corrected != word:
                    break
            
            corrected_words.append(corrected)

        return " ".join(corrected_words)
    


schema_info = {
    "Compliance": {
        "ComplianceID": [],
        "ComplianceType": ["Accounting", "Technical", "Reporting", "Tax","Functional"],
        "ComplianceTypeId": [],
        "MinCredits": []
    },
    "Employee": {
        "EmpId": [],
        "UserName": [],
        "MailId": [],
        "UserStatus": ["Active","LOP","Terminated"],
        "UserType": ["Contractual", "Partner", "Permanent"],
        "ComplianceID": [],
    },
    "UserDashboard": {
        "UserId": [],
        "ReportingPeriod": [],
        "RPStartDate": [],
        "RPEndDate": []
    },
    "Creator":{
        "creatorId":[],
        "creatorName":[],
        "isExternal": [],
        "employeeId":[]
    },
    "Instructor":{
        "instructorId":[],
        "instructorName":[],
        "isExternal": [],
        "empId":[]
    },
    "Course": {
        "Title": [],
        "CourseCode": [],
        "Type": ["Internal", "External", "Local", "Online"],
        "StartTime": [],
        "EndTime": [],
        "MaxCPE": [],
        "Instructor": [],
        "Status": ["In Review", "Live", "Retired"],
        "Creator": [],
        "StatusDate": [],
        "ComplianceID": [],
        "InstructorId":[],
        "CreatorId":[]
    },
    "Credit": {
        "CourseCode": [],
        "UserId": [],
        "AwardedCPE": [],
        "CompletionDate": [],
        "AwardType": ["Learner", "Instructor", "Reviewer"],
        "IsProcessed": []
    }
}

spelling_corrector = EnhancedSpellingCorrector(schema_info)


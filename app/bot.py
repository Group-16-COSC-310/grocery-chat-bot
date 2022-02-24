from google.cloud import dialogflow
from app.products.product_info import ProductInfo
from app.products.product_info import StoreInfo
from app.concerns.further_concern import OtherConcerns
class Bot:

    # def __init__(self):
    #     self.greeting()

    # def greeting(self):
    #     print("Hi!")
    #     options = "Please choose from one of the following options:\n a)Store information\n b)Product information\n c)Other concerns\n d)Exit"
    #     while(True):
    #         print(options)
    #         userInput = input().lower()
    #         if(userInput not in ["a","b","c","d","a)","b)","c)","d)"]):
    #             print("Incorrect input! Please enter a,b or c: ")
    #         else:
    #             if(userInput in ["a","a)"]):
    #                 self.getStoreInfo()
    #             elif(userInput in ["b","b)"]):
    #                 self.getProductInfo()
    #             elif(userInput in ["c","c)"]):
    #                 self.getCustomerService()
    #             else:
    #                 print("Goodbye!")
    #                 break
    #             print("Is there anything else I could help you with?")



    # def getStoreInfo(self):
    #     print("store info")

    # def getCustomerService(self):
    #     print("customer service info")
    
    # def getProductInfo(self):
    #     print("product info")

    
    def detect_intent_texts(self,text, project_id = "grocery-chat-bot", session_id = "test", language_code = "en-US"):
      """Returns the result of detect intent with texts as inputs.

      Using the same `session_id` between requests allows continuation
      of the conversation."""
      
      session_client = dialogflow.SessionsClient()

      session = session_client.session_path(project_id, session_id)
      print("Session path: {}\n".format(session))

      text_input = dialogflow.TextInput(text=text, language_code=language_code)

      query_input = dialogflow.QueryInput(text=text_input)

      response = session_client.detect_intent(
          request={"session": session, "query_input": query_input}
      )
      
      #route_to_handler(response.query_result.intent.display_name,text)

      print("=" * 20)
      print("Query text: {}".format(response.query_result.query_text))
      print(
          "Detected intent: {} (confidence: {})\n".format(
              response.query_result.intent.display_name,
              response.query_result.intent_detection_confidence,
          )
      )
      print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))

    #Based on intent, route to appropriate handler
    def route_to_handler(self, intentDetected ,userText):
        #If the question is about (detected intent) product info, direct it to the product information handler.  
        if(intentDetected == "product-info"):
            #if object for product-info is not already in the intents map, create a new object. Else invoke handler using existing object.
            if(not self.intents["product-info"]):
                prodObj = ProductInfo()
                self.intents["product-info"]=prodObj
            prodObj.prodHandler(userText)

        #If the question is about (detected intent) store info, direct it to the store information handler. 
        elif(intentDetected == "store-info"):
            #if object for store-info is not already in the intents map, create a new object. Else invoke handler using existing object.   
            if(not self.intents["store-info"]):     
                storeObj = StoreInfo()      
                self.intents["store-info"]=storeObj    
            storeObj.storeHandler(userText)

        #If intent cannot be detected, direct it to the other concerns handler   
        else:
            #if object for other-concerns is not already in the intents map, create a new object. Else invoke handler using existing object. 
            if(not self.intents["other-concerns"]):     
                concernsObj = OtherConcerns()      
                self.intents["other-concerns"]=concernsObj 
            storeObj.concernsHandler(userText)




    
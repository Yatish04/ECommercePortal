
class Transaction(object):
    def __init__(self,type_,number):
        if type_ == "creditcard":
            self.creditcard = number
        if type_ == "debitcard":
            self.debitcard = number
        self.cashondelivery = 0
        self._commit()
        
        
        
    # Start of user code -> properties/constructors for Transaction class

    # End of user code
    def _commit(self):
        # Start of user code protected zone for commit function body
        transdict={"status":True}
        self.trans=transdict
        return 
        # End of user code
    def get_status(self):
        return self.trans["status"]	
	
    def _rollback(self):
        # Start of user code protected zone for rollback function body
        trans_dict={"status":False}
        return trans_dict
        # End of user code	
    

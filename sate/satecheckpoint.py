'''
Created on Oct 20, 2011

@author: smirarab
'''
import os
import pickle
import shutil

class CheckPointState(object):
    '''
    The state of the SATe, as releveant to the checkpointign feauture
    '''
    INIT = "init"
    
    def __init__(self):
        '''
        Constructor
        '''
        self.best_tree = None
        self.best_dataset = None
        self.best_score = None
        
        self.last_tree = None
        self.last_dataset= None
        self.last_score = None
        
        self.curr_iter = None
        self.num_iter_since_imp = None
        self.is_stuck_in_blind = False
        self.switch_to_blind_iter = None
        self.blindmode_trigger = None
        
        self.tmp_root = None
        
        self.new_dataset = None
        
class CheckPointManager:
    
    def __init__(self):
        # TODO: remove the following line (it's here to help my IDE)
        self.checkpoint_state = CheckPointState()
        self.checkpoint_state = None
        self._ckcpt_path = None
        self.is_recovering = False 
    
    def save_checkpoint(self):
        assert os.path.exists(self._ckcpt_path)
        info_path = os.path.join(self._ckcpt_path,"info")        
        pickle.dump(self.checkpoint_state, open(info_path,"w"))
        
    def restore_checkpoint(self):
        assert os.path.exists(self._ckcpt_path)   
        info_path = os.path.join(self._ckcpt_path,"info")
        assert os.path.exists(info_path)
        self.checkpoint_state = pickle.load(open(info_path))        
        
    def initiate_ckpt_state(self,ckpt_path):
        self._ckcpt_path = ckpt_path
        if not os.path.exists(self._ckcpt_path):
            os.makedirs(self._ckcpt_path)        
            self.checkpoint_state = CheckPointState()
        else:                            
            self.restore_checkpoint()
            self.is_recovering = True
    
    def is_checkpointing(self):
        return self.checkpoint_state != None

    def remove_checkpoint_path(self):
        shutil.rmtree(self._ckcpt_path) 
    
checkpoint_manager = CheckPointManager()
#def get_checkpoint_manager():
#    if _checkpoint_manager is None:
#        _checkpoint_manager = CheckPointManager()
#    return _checkpoint_manager
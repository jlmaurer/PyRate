'''
# my original ideas about checking if floats are equal...
# check if match to a certain number of decimal places
if truncate(m1[it].item(),1) != truncate(m2[it].item(),1):
    er_str += ' '*8+'* do not match to precision @ '+str(it)+'\n'
    er_str += ' '*12+'* m1 = '+str(Decimal(m1[it].item()))+'\n'
    er_str += ' '*12+'* m2 = '+str(Decimal(m2[it].item()))+'\n'
'''
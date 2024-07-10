import numpy as np

def adjustArrays(ms, hs, w):
    rowsHS, colsHS, bandsHS = hs.shape
    rowsMS, colsMS, bandsMS = ms.shape
    
    
    newRowsHS, newRowsMS = adjust_numbers(rowsHS, rowsMS, w)
    
    newColsHS, newColsMS = adjust_numbers(colsHS, colsMS, w)
    
    return cutArray(ms, (newRowsMS, newColsMS)), cutArray(hs, (newRowsHS, newColsHS))
    

def cutArray(arr, newShape):
    _, _, bands = arr.shape
    rows, cols = newShape
    
    newArray = np.zeros((rows, cols, bands))
    
    
    for i in range(bands):
        tmp = arr[:,:,i]
        tmp = tmp[:rows, :cols]
        newArray[:,:,i] = tmp
        
    return newArray
        
def adjust_numbers(a, b, w):
    if a*w == b:
        return (a,b)
    

    if a*w < b:
        while not a*w == b:
            b -= 1
        return a, b
    else:
        a -= 1
        return adjust_numbers(a, b, w)




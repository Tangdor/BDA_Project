from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
class TTTField():
 def __init__(self,xCoordinate, yCoordinate,id,marked,winner):
     self.xCoordinate = xCoordinate
     self.yCoordinate = yCoordinate
     self.id          = id
     self.marked      = marked
     self.winner      = winner
 def setMarker (self,marker,image):
    if marker == "X":
     if self.marked == False:
      print ("hello ich markiere x")
      font = ImageFont.truetype("FreeMonoBold.ttf", 40)
      draw = ImageDraw.Draw(image)
      draw.text((self.xCoordinate+8,self.yCoordinate), "X", fill="red", font=font)
      self.marked = True
      self.winner = "X"
     else:
      return image
    elif marker == "O":
     if self.marked == False:
      print ("hello ich markiere o")
      font = ImageFont.truetype("FreeMonoBold.ttf", 40)
      draw = ImageDraw.Draw(image)
      draw.text((self.xCoordinate+8,self.yCoordinate), "O", fill="red", font=font)
      self.marked = True
      self.winner = "O"
     else:
      return image
    return image
 def redField(self,image):
    draw = ImageDraw.Draw(image)
    draw.rectangle([(self.xCoordinate,self.yCoordinate), (self.xCoordinate+40,self.yCoordinate+40)], None,'red')
    return image
 def whiteField(self,image):
    draw = ImageDraw.Draw(image)
    draw.rectangle([(self.xCoordinate,self.yCoordinate), (self.xCoordinate+40,self.yCoordinate+40)], None, 'white')
    return image

"""Render the delivered manuscripts for ordinary visual layout review."""
from pathlib import Path
import pymupdf
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent
DEST=ROOT/'build/pdf_review'; DEST.mkdir(exist_ok=True)
for name,path in [('main',ROOT/'manuscript/main.pdf')]:
 doc=pymupdf.open(path)
 previews=[]
 for i,page in enumerate(doc):
  pix=page.get_pixmap(matrix=pymupdf.Matrix(1.45,1.45),alpha=False)
  pix.save(DEST/f'{name}_{i+1:02d}.png')
  im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
  im.thumbnail((330,470))
  card=Image.new('RGB',(350,505),'#eeeeee'); card.paste(im,((350-im.width)//2,20))
  ImageDraw.Draw(card).text((15,482),f'{name}: page {i+1}',fill='black'); previews.append(card)
 for offset in range(0,len(previews),6):
  sheet=Image.new('RGB',(1050,1010),'white')
  for j,im in enumerate(previews[offset:offset+6]): sheet.paste(im,((j%3)*350,(j//3)*505))
  sheet.save(DEST/f'{name}_overview_{offset//6+1:02d}.png')
 fonts={font[0] for page in doc for font in page.get_fonts()}
 embedded=[doc.extract_font(xref)[1] != 'n/a' and bool(doc.extract_font(xref)[3]) for xref in fonts]
 print(name,'pages=',len(doc),'all_fonts_embedded=',all(embedded),'figure_pages=',sum('Figure ' in p.get_text() for p in doc))
 print('Main figure/table pages:',[(i+1) for i,p in enumerate(doc) if 'Figure ' in p.get_text() or 'Table ' in p.get_text()])

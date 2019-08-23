from HanTa.HanoverTagger import  TrainHanoverTagger
import codecs
import os

#trainer =   TrainHanoverTagger()
#datafile = codecs.open("labeledmorph_ger.csv", "r","utf-8")
#trainer.load(datafile)
#datafile.close()  
#trainer.train_model(observed_values = False)
#trainer.write_model('morphmodel_ger_pure.pgz')
  
trainer =   TrainHanoverTagger()
datafile = codecs.open("labeledmorph_ger.csv", "r","utf-8")
trainer.load(datafile)
datafile.close()  
trainer.train_model(observed_values = True)
#trainer.write_model('morphmodel_ger_hybrid.pgz')
trainer.write_model('morphmodel_ger.pgz')

if os.path.exists('HanTa/morphmodel_ger.pgz'):
   os.remove('HanTa/morphmodel_ger.pgz')
os.rename('morphmodel_ger.pgz','HanTa/morphmodel_ger.pgz')
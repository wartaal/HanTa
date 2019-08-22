from HanoverTagger import  TrainHanoverTagger
import codecs

trainer =   TrainHanoverTagger()
datafile = codecs.open("labeledmorph_ger.csv", "r","utf-8")
trainer.load(datafile)
datafile.close()  
trainer.train_model(observed_values = False)
trainer.write_model('morphmodel_ger_pure.pgz')
  
trainer =   TrainHanoverTagger()
datafile = codecs.open("labeledmorph_ger.csv", "r","utf-8")
trainer.load(datafile)
datafile.close()  
trainer.train_model(observed_values = True)
trainer.write_model('morphmodel_ger_hybrid.pgz')
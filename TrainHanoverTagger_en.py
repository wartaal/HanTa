from HanoverTagger import  TrainHanoverTagger
import codecs

 
trainer =   TrainHanoverTagger()
datafile = codecs.open("en/labeledmorph_en.csv", "r","utf-8")
trainer.load(datafile)
datafile.close()  
trainer.train_model(observed_values = True)
trainer.write_model('morphmodel_en.pgz')
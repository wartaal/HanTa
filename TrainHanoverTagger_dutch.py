from HanoverTagger import  TrainHanoverTagger
import codecs

 
trainer =   TrainHanoverTagger()
datafile = codecs.open("nl/labeledmorph_dutch.csv", "r","utf-8")
trainer.load(datafile)
datafile.close()  
trainer.train_model(observed_values = True)
trainer.write_model('morphmodel_dutch.pgz')
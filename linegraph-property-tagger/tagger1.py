import web
from web import form
import os,shutil
import json 
import csv

render = web.template.render('templates/')
pngs=os.listdir(os.path.join(os.getcwd(),'pngs'))
pngindex=-1

urls = ('/', 'index')
app = web.application(urls, globals())


class MyForm(web.form.Form):
    def render(self):
        out = "<p>"
        #print self.inputs,type(self.inputs)
        for i in self.inputs[:-1]:
            #out += '<span>'+i.pre+i.render()+i.post+'</span>'
            out += '<span>'+i.description+" : "+i.render()+'</span>'
        out+="</p><p>"+self.inputs[-1].render()+"</p>"
        return out

myform = MyForm( 
    form.Dropdown('tosplit', ['Y', 'N']),
    form.Dropdown('ideal', ['Y', 'N']),
    form.Dropdown('chromatic number', ['1', '>1']),
    form.Dropdown('continuity', ['Y', 'N']),
    form.Dropdown('intersect', ['Y', 'N']),
    form.Dropdown('overlap', ['Y', 'N']),
    form.Textarea('description',rows=20, cols=50)) 



'''
class myform(form.Form):
    #inputs=[]
    self.inputs.append(form.Dropdown('tosplit', ['Y', 'N']))
    self.inputs.append(form.Dropdown('ideal', ['Y', 'N']))
    self.inputs.append(form.Dropdown('chromatic number', ['1', '>1']))
    self.inputs.append(form.Dropdown('continuity', ['Y', 'N']))
    self.inputs.append(form.Dropdown('intersect', ['Y', 'N']))
    self.inputs.append(form.Dropdown('overlap', ['Y', 'N']))
    self.inputs.append(form.Textarea('description',rows=20, cols=50))

    def render(self):
        out = ""
        print self.inputs,type(self.inputs)
        for i in self.inputs:
            out += '<span>'+i.pre+i.render()+i.post+'</span>'
        return out

'''
    
def writeToCSV(im,ideal,cn,cont,intsect,ol,desc):
        with open('results.csv', 'a') as fp:
            a = csv.writer(fp, delimiter=',')
            data = [im,ideal,cn,cont,intsect,ol,desc]
            a.writerow(data) 

class index: 
    def GET(self): 
        form = myform()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
	return render.formtest(form,"desc")
     
    def POST(self):
        global pngindex
        pngindex+=1 
        form = myform() 
        if not form.validates(): 
            return render.formtest(form,"desc")
        else:
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.
            #return "Grrreat success! chromatic number: %s, conituity: %s, intersect: %s, overlap: %s, desc: %s " % \
            shutil.copy(os.path.join("pngs",pngs[pngindex]),"static/temp.png")
            print pngindex, pngs[pngindex],pngs[0]
            writeToCSV(pngs[pngindex],form['ideal'].value,form['chromatic number'].value,form['continuity'].value,\
            form['intersect'].value,form['overlap'].value,form['description'].value)
            desc="desc"
            try:
                desc=json.load(open(os.path.join("jsons",pngs[pngindex][:-8]+".json")))['Caption']
            except:
                print os.path.join("jsons",pngs[pngindex][:-8]+".json"),"error"
            return render.formtest(form,desc)

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()

    '''
    form.Textbox("boe"), 
    form.Textbox("bax", 
        form.notnull,
        form.regexp('\d+', 'Must be a digit'),
        form.Validator('Must be more than 5', lambda x:int(x)>5)),
    form.Checkbox('color'),
    '''

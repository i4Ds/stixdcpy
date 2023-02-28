#!/usr/bin/python3
import tempfile
import numpy as np
import webbrowser
try:
    import IPython
    from IPython.display import display, HTML
    from IPython.display import Javascript
except ImportError:
    pass
class DetectorView(object):
    def __init__(self):
        self.counts=[0]*384
        self.toolbar_enabled='true'
        self.is_jupyter_env=False
        self.js_url="https://datacenter.stix.i4ds.net/static/js/pystix.js" 
        self.js2=''

        try:
            if 'ipykernel' in str(IPython.get_ipython()):
                self.is_jupyter_env=True
        except Exception :
            pass


    def get_html(self):
        self.js2=f'''
        $(document).ready(function() {{
            StixDetectorView.showGridParameterOnHover(true);
            StixDetectorView.plotDetector("#dv", {{
            counts:  {self.counts}, vW: 1140,
            vH: 1140,
            legend: false,
            detectorViewToolbar: {self.toolbar_enabled},
            reset:true}});
            $("#save").on("click",function() {{StixDetectorView.saveSVG();}});
        }}); 	
        '''
        head='''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>  <title>STIX detector view</title>
        '''
        js1=f'''<script src="{self.js_url}" type="text/javascript"></script>'''
        css='''
            <link rel="stylesheet" href="https://datacenter.stix.i4ds.net/static/css/pystix.css">
            <style>
        .center {
          display: flex;
          justify-content: center;
          align-items: center;
        }
        #copy-data{display:none;}
        </style>
        '''
        container='''
        <div class="center">
            <button type="button" id="save" >Save as SVG</button>
        </div>
        <div id="dv" style="width:500px;" >Please execute the cell again if you see this message!</div>
        '''
        if not self.is_jupyter_env:
            html=f'{head} {css}  {js1} </head><body> {container} <script>{self.js2}</script></body></html>'
        else:
            html=f'<div>{css} {js1}{container} <script>{self.js2}</script></div>'
        return html
    def plot(self, pixel_counts, toolbar=True):
        """
        Generate a detector view figure. 
        Parameters
        -------------
        pixel_counts: list or numpy.array
            counts of 384 pixels
        toolbar: boolean
            display the toolbar on the plot if True. 
        Returns:
            None
        """
        if toolbar and self.is_jupyter_env:
            display(HTML('''<div style="border: 1;color: #ffc107!important; " >The toolbar allows normalizing counts in an interactive way. 
                    Unfortunately, this feature is not available in the Jupyter notebook environment. To use the feature, please run d.save("detector_view.html")
                    to save the figure a html file, and then open the saved file with a web browser</div>'''))
            #toolbar=False

        self.toolbar_enabled='false' if not toolbar else 'true'
        if isinstance(pixel_counts, np.ndarray):
            pixel_counts=pixel_counts.flatten().tolist()

        if len(pixel_counts)!=384:
            raise ValueError('counts must be a list of length 384')
        self.counts=pixel_counts
        html=self.get_html()
        if self.is_jupyter_env:
            display(HTML(html))
            return
        #not in notebook
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
            temp_file.write(html.encode('utf-8'))
            temp_file.close()
            webbrowser.open_new_tab(temp_file.name)

    def save(self, filename='detector_view.html'):
        """
        Save the figure to the specified html file. 
        One can open the html file using a web browser and export the figure to SVG format by clicking the button 
        """
        if not filename.endswith('html'):
            filename+='html'
        with open(filename,'w') as f:
            f.write(self.get_html())
            print(f'Saved to {filename}. One can open it with a web browser and export it to SVG format')

def test():
    counts=[i for i in range(384)]
    dv=DetectorView()
    dv.plot(counts)


if __name__=='__main__':
    test()



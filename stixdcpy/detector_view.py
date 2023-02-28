#!/usr/bin/python3
import tempfile
import webbrowser
class DetectorView(object):
    def __init__(self):
        self.counts=[0]*384
        self.toolbar_enabled='true'
    def _repr_html_(self):
        return self.get_html()

    def get_html(self):
        html=f'''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
    <head>  <title>STIX detector view</title>
        <script src="https://datacenter.stix.i4ds.net/static/js/pystix.js" type="text/javascript"></script>
    <style>
    .center {{
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    #pixel-filter{{display:none;}}
    #copy-data{{display:none;}}
    </style>
        </head>
        <body>
        <div class="center">
            <button type="button" id="save" >Save as SVG</button>
        </div>
        <div id="detector-view" style="width:500px;" >Rendering...</div>
        </body>
        <script>
        $(document).ready(function() {{
            StixDetectorView.showGridParameterOnHover(true);
            StixDetectorView.plotDetector("#detector-view", {{
            counts:  {self.counts}, vW: 1140,
            vH: 1140,
            legend: false,
            detectorViewToolbar: {self.toolbar_enabled},
            reset:true
        }}); 
        $("#save").on("click",function() {{StixDetectorView.saveSVG();}});

        }});
        </script>
        </html>
        '''
        return html
    def plot(self, pixel_counts:list, toolbar=True):
        """
        Generate a detector view figure. 
        Parameters
        -------------
        pixel_counts: list
            counts of 384 pixels
        toolbar: boolean
            display the toolbar on the plot if True. 
        Returns:
            None
        

        """
        self.toolbar_enabled='false' if not toolbar else 'true'

        if len(pixel_counts)!=384:
            raise ValueError('counts must be a list of length 384')
        self.counts=pixel_counts
        html=self.get_html()
        try:
            import IPython
            from IPython.display import display, HTML

            if 'ipykernel' in str(IPython.get_ipython()):
                display(HTML(html))
                return 
        except Exception:
            pass
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



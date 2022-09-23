#!/usr/bin/python3
import numpy as np
from matplotlib import pyplot as plt


class DetectorView(object):
    CANVAS_W = 1005
    CANVAS_H = 1105
    VIEW_W = int(3 * CANVAS_W)
    VIEW_H = int(3 * CANVAS_H)
    VIEWBOX = f'0  0 {VIEW_W} {VIEW_H}'
    RFRAME = 450
    RASPECT = 70
    P0 = np.array([CANVAS_W / 2., CANVAS_H - RFRAME - 5])
    WHITE = 'rgb(255,255,255)'

    def __init__(self,
                 pixel_counts=np.zeros(384),
                 cmap='viridis',
                 colorbar=False,
                 logscale=False):
        """
         Plot STIX detector
         Parameters
          pixel_counts: 1x384 np.array or a 32x12 np.array
            
            counts in 384 pixels
          cmap:  str, optional
            matploat colormap, for example viridis, plasma, etc.
          colorbar: bool
            Plot colobar if it is True 
         Returns
           python object
        """

        self.cmap_name = cmap
        pixel_counts = pixel_counts.flatten()
        self.pixel_counts = pixel_counts
        col = (np.array(plt.get_cmap(cmap).colors) * 256).astype(int)
        self.color_map = [f'rgb({x[0]},{x[1]},{x[2]})' for x in col]
        self.color_x = np.linspace(0, 1, len(self.color_map))

        self.colors = [self.WHITE] * 384

        self.vis_counts = pixel_counts if not logscale else np.log(
            pixel_counts,
            where=np.array(pixel_counts) > 0,
            out=np.zeros_like(pixel_counts))
        if np.max(self.vis_counts) > 0:
            max_val = np.max(self.vis_counts)
            min_val = np.min(self.vis_counts)
            if max_val > min_val:
                nx = (self.vis_counts - min_val) / (max_val - min_val)
                self.colors = np.array([
                    self.color_map[np.argmin(np.abs(y - self.color_x))]
                    for y in nx
                ])
        self.svg = self.create_detector_svg(colorbar)
        self.html = f'<div style="width:400px;height:400px;">{self.svg}</html>'

    def get_html(self):
        return self.html

    def get_svg(self):
        """
        get svg string
        """
        return self.svg

    def save(self, filename):
        """
            save detector view to a svg file
        Parameters:
          filename: str
            svg filename
        Returns None
        """
        with open(filename, 'w') as f:
            f.write(self.svg)

    def display(self):
        """
         Plot detector in nootbook
        """
        try:
            from IPython.display import SVG
        except ImportError:
            print('IPython not installed. Can not display the detector view')
            return
        return SVG(self.svg)

    def _create_color_bar(self, x0, y0, width, height):
        path = (
            '<rect x="{x0}" y="{y0}" width="{width}" height="{height}"'
            'style="fill:rgb(250,250,250); stroke-width:0;stroke:rgb(0,0,255)" />'
        ).format(x0=x0, y0=y0, width=width, height=height)
        num = len(self.color_map)
        dl = width / num
        max_value = np.max(self.pixel_counts)
        for i, col in enumerate(self.color_map):
            x = dl * i + x0
            y = y0
            path += '<rect x="{}" y="{}" width="{}" height="{}"  style="fill:{}; stroke-width:1;stroke:{}" />'.format(
                x, y, dl, height, col, col)
        num_ticks = 10
        for i in range(0, num_ticks):
            x = dl * i + x0
            y = y0 - 20
            path += '<text x="{}" y="{}" > {} </text>'.format(
                x, y, max_value * i / num_ticks)

        return path

    def create_detector_svg(self, colorbar=True):
        positions = [[135, 412.5], [135, 527.5], [135, 662.5], [135, 777.5],
                     [260, 297.5], [260, 412.5], [260, 527.5], [260, 662.5],
                     [260, 777.5], [260, 892.5], [385, 227.5], [385, 342.5],
                     [385, 457.5], [385, 732.5], [385, 847.5], [385, 962.5],
                     [510, 227.5], [510, 342.5], [510, 457.5], [510, 732.5],
                     [510, 847.5], [510, 962.5], [635, 297.5], [635, 412.5],
                     [635, 527.5], [635, 662.5], [635, 777.5], [635, 892.5],
                     [760, 412.5], [760, 527.5], [760, 662.5], [760, 777.5]]
        svg_start = '''
            <svg width="{cw}" height="{ch}" viewBox="{view_box}">
          <circle
              style="opacity:0.1;fill:#0000ff;stroke:#0000ff;stroke-width:1.046;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
             id="path5200"
             cx="{x0}"
             cy="{y0}"
             r="{r_frame}"/>
          <path  style="stroke-width:3;stroke:rgb(0,0,250)"  d="M{x0} {y_min} L{x0} {y_max} " />
          <path  style="stroke-width:3;stroke:rgb(0,0,250)"  d="M{x_min} {y0} L{x_max} {y0}" />
      <circle
         style="opacity:0.95999995;fill:#222b00;stroke:#0000ff;stroke-width:1.046;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
         id="path5204"
         cx="{x0}"
         cy="{y0}"
         r="{r_aspect}" />
          '''.format(cw=self.CANVAS_W,
                     ch=self.CANVAS_H,
                     view_box=self.VIEWBOX,
                     x0=self.P0[0],
                     y0=self.P0[1],
                     y_min=self.P0[1] - self.RFRAME,
                     r_frame=self.RFRAME,
                     r_aspect=self.RASPECT,
                     y_max=self.P0[1] + self.RFRAME,
                     x_min=self.P0[0] - self.RFRAME,
                     x_max=self.P0[0] + self.RFRAME)

        svg_end = '   </svg>'

        color_bar = ''
        if colorbar:
            color_bar = self._create_color_bar(10, 100, 1000, 30)
        template = svg_start + color_bar + '{}' + svg_end
        items = []
        for i, pos in enumerate(positions):
            pos[1] = pos[1] + 5
            items.append(self.create_one_detector_svg(i, pos, '{}'))

        return template.format('\n'.join(items))

    def create_one_detector_svg(self,
                                detector_id=0,
                                start=(0, 0),
                                svg_template=''):
        """ data is a 32*12 array """

        if not svg_template:
            svg_template = """
            <svg width="110" height="110">
            {}
            </svg>
            """
        group = ''

        pixel_template = '''
          <path id="{}" text="" style="fill:{};stroke-width:1;stroke:rgb(200,200,200)"
          d="{}" ><title>{}</title></path>'''

        start_x = start[0]
        start_y = start[1]
        offset = np.array([start_x, start_y])
        fill_color = 'rgb(230,230,230)'

        pitch_x = 22
        pitch_y = 46

        big_p0_top = offset + np.array([6, 4])
        big_p0_bottom = offset + np.array([6, 4 + 92])

        big_pixel_top = 'h 22 v 46 h -11 v -4.5 h -11 Z'
        big_pixel_bottom = 'h 22 v -46 h -11 v 4.5 h -11 Z'

        small_p0 = offset + np.array([6, 50 - 4.5])
        small_pixel_path = 'h 11 v 9 h -11  Z'

        container = []
        #create big pixels

        guardring = '<rect x="{}" y="{}" width="100" height="100"  style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)" />'.format(
            offset[0], offset[1])
        x0 = offset[0]
        y0 = offset[1]
        #print("'det_{}':'M{} {} L {} {} L{} {} L{} {} Z ',".format(detector_id,x0,y0,x0+100,y0,x0+100,y0+100, x0,y0+100))
        container.append(guardring)
        text = '<text x="{}" y="{}" filled="red"> #{} </text>'.format(
            offset[0] + 40, offset[1] + 110, detector_id + 1)
        container.append(text)

        for i in range(0, 4):
            start = big_p0_top + np.array([i * pitch_x, 0])
            path = 'M {} {} {}'.format(start[0], start[1], big_pixel_top)
            pid = 'id-{}-{}'.format(detector_id, i)
            pid = detector_id * 12 + i
            counts = self.pixel_counts[pid]
            fill_color = self.colors[pid]

            container.append(
                pixel_template.format(pid, fill_color, path, counts))

        for i in range(0, 4):
            start = big_p0_bottom + np.array([i * pitch_x, 0])
            path = 'M {} {} {}'.format(start[0], start[1], big_pixel_bottom)
            pid = 'id-{}-{}'.format(detector_id, i + 4)
            pid = detector_id * 12 + i + 4
            counts = self.pixel_counts[pid]
            fill_color = self.colors[pid]

            container.append(
                pixel_template.format(pid, fill_color, path, counts))

        for i in range(0, 4):
            start = small_p0 + np.array([i * pitch_x, 0])
            path = 'M {} {} {}'.format(start[0], start[1], small_pixel_path)
            pid = 'id-{}-{}'.format(detector_id, i + 8)
            pid = detector_id * 12 + i + 8
            counts = self.pixel_counts[pid]
            fill_color = self.colors[pid]
            container.append(
                pixel_template.format(pid, fill_color, path, counts))
        group = '<g> {} </g>'.format('\n'.join(container))
        return svg_template.format(group)


if __name__ == '__main__':
    with open('detector.svg', 'w') as f:
        data = np.arange(384)
        det = DetectorView(data)
        f.write(det.get_svg())

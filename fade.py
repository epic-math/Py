# fade.py
# This code creates two slides with fade-in and fade-out
import os
import sys
import subprocess
import psutil

class mytool:
    def __init__(self):
        self.count = 0
        self.copied_file = ['./in001.png', './in002.png']

    def add_fade_effect(self, filename):
        # make two frames : at the beginning and at the end
        # this is done by copying one I-Frame for a slide
        # then adding fades at both ends
        for f in self.copied_file:
            cmd = map(lambda x: '%s' %x, ['cp', filename, f])
            subprocess.call(cmd)

        # make normal slide
        # ffmpeg -r 1/5 -i in%03d.png -c:v libx264 -r 30 -y -pix_fmt yuv420p slide.mp4 
        in_framerate = 1./5
        out_framerate = 30
        cmd = ['ffmpeg', '-r', in_framerate, '-i','in%03d.png','-c:v','libx264',
              '-r', out_framerate, '-y','-pix_fmt','yuv420p','slide.mp4']
        cmd = map(lambda x: '%s' %x, cmd)
        subprocess.call(cmd)

        # add fade-in effect - from 0th to 30th frame
        #ffmpeg -i slide.mp4 -y -vf fade=in:0:30 slide_fade_in.mp4
        cmd = ['ffmpeg', '-i','slide.mp4','-y','-vf','fade=in:0:30','slide_fade_in.mp4']
        subprocess.call(cmd)

       # add fade-out effect to the slide that has fade-in effect already : 30 frames starting from 120th  
        #ffmpeg -i slide_fade_in.mp4 -y -vf fade=out:120:30 slide_fade_in_out.mp4 
        cmd = ['ffmpeg', '-i','slide_fade_in.mp4','-y','-vf','fade=out:120:30', 'slide_fade_in_out.mp4']
        subprocess.call(cmd)

        # rename the output to 'final#.mp4'
        slide_name = 'final'+str(self.count)+'.mp4'
        cmd = map(lambda x: '%s' %x, ['cp', 'slide_fade_in_out.mp4', slide_name])
        subprocess.call(cmd)

        # remove the copied files
        for f in self.copied_file:
            cmd = map(lambda x: '%s' %x, ['rm','-f', f])
            subprocess.call(cmd)

        self.count += 1

    # get the list of file and feed one file at a time to "add_fade_effect()"
    def file_list(self, dir):
        basedir = dir
        subdir = []
        slides = []
        for item in os.listdir(dir):
            fullpath = os.path.join(basedir, item)
            if os.path.isdir(fullpath):
                subdir.append(fullpath)
            else:
               if item.endswith(".png"):
                   slides.append(fullpath)

        for slide in slides:
            self.add_fade_effect(slide)

if __name__ == "__main__":

    if len(sys.argv) <= 1:
        path = '.'
    else:
        path = sys.argv[1]
    m = mytool()
    m.file_list(path)

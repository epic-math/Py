#!/usr/bin/python

import psutil
import simplejson
import subprocess

procs_id = 0
procs = {}
procs_data = []

def getMetadata(video):
    cmd = ['ffprobe', '-show_streams', '-show_packets', '-print_format', 'json', video]
    print 'cmd=', cmd
    stdout = runCommand(cmd, return_stdout = True, busy_wait = False)
    data = simplejson.loads(stdout)
    metadata = { }

    if data:
        # Obtain duration here
        if 'streams' in data:
            for item in data['streams']:
                if 'codec_type' in item and 'duration' in item and 'video' in item['codec_type']:
                    metadata['duration'] = float(item['duration'])
        else:
            metadata['duration'] = float(0)

        # Obtain iframes here
        iframes = []
        if 'packets' in data:
            # Filter out packet types
            video_packets = sorted(
                [packet for packet in data['packets'] if (packet['codec_type'] == "video" and 'pos' in packet)],
                key = lambda packet: int(packet['pos'])
            )
            video_positions = sorted([int(packet['pos']) for packet in video_packets])
            audio_packets = sorted(
                [packet for packet in data['packets'] if (packet['codec_type'] == "audio" and 'pos' in packet)],
                key = lambda packet: int(packet['pos']))
            audio_positions = sorted([int(packet['pos']) for packet in audio_packets])

            # Search for iframes
            iframe_packets = [packet for packet in video_packets if (packet['flags'] == "K")]
            positions = sorted([int(packet['pos']) for packet in data['packets'] if ('pos' in packet)])

            start_byte = 0
            end_byte = 0
            duration = None

            for iframe in iframe_packets:
                start_byte = int(iframe['pos'])
                end_byte = 0

                for pos in positions:
                    if pos > start_byte:
                        end_byte = pos - 188
                        break

                if duration is None:
                    duration = float(iframe['pts_time'])
                else:
                    new_duration = float(iframe['pts_time'])
                    iframes.append({ 'byte_start': start_byte,
                                     'byte_end': end_byte,
                                     'duration': (new_duration - duration) })
                    duration = new_duration

            last_duration = float(video_packets[-1]['pts_time'])
            iframes.append({ 'byte_start': start_byte,
                             'byte_end': end_byte,
                             'duration': last_duration - duration })
        metadata['iframes'] = iframes
        print 'metadata=',metadata

    return metadata


# Runs command silently
def runCommand(cmd, use_shell = False, return_stdout = False, busy_wait = True, poll_duration = 0.5):
    # Sanitize cmd to string
    cmd = map(lambda x: '%s' % x, cmd)
    if use_shell:
        command = ' '.join(cmd)
    else:
        command = cmd

    if return_stdout:
        proc = psutil.Popen(cmd, shell = use_shell, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    else:
        proc = psutil.Popen(cmd, shell = use_shell, 
                                stdout = open('/dev/null', 'w'),
                                stderr = open('/dev/null', 'w'))


    global procs_id 
    global procs
    global procs_data
    proc_id = procs_id
    procs[proc_id] = proc
    procs_id += 1
    data = { }

    while busy_wait:
        returncode = proc.poll()
        if returncode == None:
            try:
                data = proc.as_dict(attrs = ['get_io_counters', 'get_cpu_times'])
            except Exception, e:
                pass
            time.sleep(poll_duration)
        else:
            break

    (stdout, stderr) = proc.communicate()
    returncode = proc.returncode
    del procs[proc_id]

    if returncode != 0:
        raise Exception(stderr)
    else:
        if data:
            procs_data.append(data)
        return stdout
    
if __name__ == '__main__':

    segMeta = getMetadata('video.dat')
    print 'segMeta=',segMeta
    for k in segMeta.keys():
        if(k == 'iframes'):
	    print 'iframe size =',len(segMeta[k])
            break

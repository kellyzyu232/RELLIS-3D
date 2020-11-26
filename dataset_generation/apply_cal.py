import rospy
import rosbag
import numpy as np
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import Transform, TransformStamped, Vector3, Quaternion
from std_msgs.msg import Header
import tf.transformations as tfx
from pathlib import Path
import argparse
import shutil
from tqdm import tqdm
from deconflict_tf import fix_conflicts, update_tf_chain


def main(args):
    tmp_bag = "/tmp/temp.bag"
    overwrite = args.out_bag == args.bag or not args.out_bag
    b_out = rosbag.Bag(tmp_bag, 'w') if overwrite else rosbag.Bag(args.out_bag, 'w')

    tf_static_msg = None
    tf_static_t = None
    tf_static_connection_header = None

    for topic, msg, t, cnxn_hdr in b_cal.read_messages(topics=['/tf_static', '/tf']):
        if tf_static_msg:
            tf_static_msg.transforms.extend(msg.transforms)
        else:
            tf_static_msg = msg
            tf_static_t = t
            tf_static_connection_header = cnxn_hdr
    b_cal.close()


    for topic, msg, t in b.read_messages():
        if topic == "/tf_static":
            update_tf_chain(static_tfs, msg)
        elif topic == "/tf":
            update_tf_chain(dynamic_tfs, msg)
    viz_tree('/tmp/tree_before.dot',static_tfs, dynamic_tfs)


    for b in args.bags:
        b_in = rosbag.Bag(b)
        for topic, msg, t, cnxn_hdr in tqdm(b_in.read_messages(return_connection_header=True)):
            if topic == '/tf_static':
                if tf_static_msg:
                    tf_static_msg.transforms.extend(msg.transforms)
                else:
                    tf_static_msg = msg
                    tf_static_t = t
                    tf_static_connection_header = cnxn_hdr
            else:
                b_out.write(topic, msg, t)
        b_in.close()
    b_out.write('/tf_static', tf_static_msg, tf_static_t,
                connection_header=tf_static_connection_header)
    b_out.close()

    if overwrite:
        shutil.move(tmp_bag, args.bag)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bag", nargs='+', default=[], help="bags to update")
    parser.add_argument("-c", "--cal_bag", nargs='+', default=[], help="bag with cal information in tf_static")
    parser.add_argument("-o", "--out_bag", default="",
                        help="Output ROS bag. (Default is to _overwrite_ input bag)")
    args = parser.parse_args()
    main(args)
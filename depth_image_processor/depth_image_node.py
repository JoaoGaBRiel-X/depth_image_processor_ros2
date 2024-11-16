import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import struct

class DepthImageProcessor(Node):
    def __init__(self):
        super().__init__('depth_image_processor')
        self.subscription = self.create_subscription(
            CompressedImage,
            '/depth/image_raw/compressedDepth',
            self.listener_callback,
            10)
        self.publisher = self.create_publisher(
            Image,
            '/depth/image_raw/descompressed',
            10)
        self.bridge = CvBridge()

    def listener_callback(self, msg):
        try:
            # Verifica o formato e tipo de compressão
            depth_fmt, compr_type = msg.format.split(';')
            depth_fmt = depth_fmt.strip()
            compr_type = compr_type.strip()

            if compr_type != "compressedDepth":
                self.get_logger().error("Tipo de compressão não é 'compressedDepth'.")
                return

            # Remove o cabeçalho dos dados brutos
            depth_header_size = 12
            raw_data = msg.data[depth_header_size:]

            # Decodifica a imagem de profundidade
            depth_img_raw = cv2.imdecode(np.frombuffer(raw_data, np.uint8), cv2.IMREAD_UNCHANGED)
            if depth_img_raw is None:
                self.get_logger().error("Erro ao decodificar a imagem de profundidade.")
                return

            # Converte e publica como sensor_msgs/Image
            if depth_fmt == "16UC1":
                ros_image = self.bridge.cv2_to_imgmsg(depth_img_raw, encoding='16UC1')
            elif depth_fmt == "32FC1":
                # Processar imagens em formato 32FC1 (com quantização)
                raw_header = msg.data[:depth_header_size]
                _, depthQuantA, depthQuantB = struct.unpack('iff', raw_header)
                depth_img_scaled = depthQuantA / (depth_img_raw.astype(np.float32) - depthQuantB)
                depth_img_scaled[depth_img_raw == 0] = 0
                ros_image = self.bridge.cv2_to_imgmsg(depth_img_scaled, encoding='32FC1')
            else:
                self.get_logger().error(f"Formato de profundidade '{depth_fmt}' não suportado.")
                return

            # Publica a imagem descomprimida
            ros_image.header = msg.header  # Copia o cabeçalho original
            self.publisher.publish(ros_image)

        except Exception as e:
            self.get_logger().error(f"Erro ao processar a imagem de profundidade: {e}")

def main(args=None):
    rclpy.init(args=args)
    processor_node = DepthImageProcessor()
    rclpy.spin(processor_node)
    processor_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

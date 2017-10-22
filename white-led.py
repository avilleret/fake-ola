#!/usr/bin/python3.4

import logging
import logging.handlers
import argparse
import sys
import math
import apa102
import pythonosc
from pythonosc import dispatcher
from pythonosc import osc_server

LOG_FILENAME = "/tmp/fake-ola.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

map = [  0,  1,  2,  3,  4,  5,  6,  7,
        23, 22, 21, 20, 19, 18, 17, 16,
        32, 33, 34, 35, 36, 37, 38, 39,
        55, 54, 53, 52, 51, 50, 49, 48,
        64, 65, 66, 67, 68, 69, 70, 71,

         8,  9, 10, 11, 12, 13, 14, 15,
        31, 30, 29, 28, 27, 26, 25, 24,
        40, 41, 42, 43, 44, 45, 46, 47,
        63, 62, 61, 60, 59, 58, 57, 56,
        72, 73, 74, 75, 76, 77, 78, 79]

gamma = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 ]

def red_channel(unused_addr, args, blob):
  for i in range(min(len(blob),strip.numLEDs)):
    strip.leds[i*4+3]=blob[map[i]]

def green_channel(unused_addr, args, blob):
  for i in range(min(len(blob),strip.numLEDs)):
    strip.leds[i*4+2]=blob[map[i]]

def blue_channel(unused_addr, args, blob):
  for i in range(min(len(blob),strip.numLEDs)):
    strip.leds[i*4+1]=blob[map[i]]
  strip.show()

def led_handler(unused_addr, args, blob):
  for i in range(math.floor((len(blob)-1)/3)):
    #strip.leds[i*4+3]=gamma[blob[map[i]*3]]
    #strip.leds[i*4+2]=gamma[blob[map[i]*3+1]]
    #strip.leds[i*4+1]=gamma[blob[map[i]*3+2]]
    strip.leds[i*4+3]=blob[i*3]
    strip.leds[i*4+2]=blob[i*3+1]
    strip.leds[i*4+1]=blob[i*3+2]
  strip.show()

def set_brightness(unused_addr, brightness):
  if LOG_LEVEL ==  logging.DEBUG:
    print("set brightness to {}", brightness & 0b00011111)
  b = (brightness & 0b00011111) | 0b11100000
  for i in range(strip.numLEDs):
    strip.leds[i*4]=b
  strip.show()

if __name__ == "__main__":
  parser = argparse.ArgumentParser("Fake OLA server to drive APA102 LED")
  parser.add_argument("--ip",
      default="127.0.0.1", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=7770, help="The port to listen on")
  parser.add_argument("--led",
      type=int, default=80, help="Number of LED in display")
  parser.add_argument("-d-", "--debug", action='store_true', help="Enable debug print")
  parser.add_argument("-l", "--log", help="File to write log to (default '" + LOG_FILENAME + "')")

  args = parser.parse_args()

  dispatcher = dispatcher.Dispatcher()
  dispatcher.map("/brightness", set_brightness)
  dispatcher.map("/dmx/universe/1", red_channel, "R")
  dispatcher.map("/dmx/universe/2", green_channel, "G")
  dispatcher.map("/dmx/universe/3", blue_channel, "B")
  dispatcher.map("/led", led_handler, "led")

  if args.debug:
    LOG_LEVEL = logging.DEBUG

  if args.log:
    LOG_FILENAME = args.log

  # Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
  # Give the logger a unique name (good practice)
  logger = logging.getLogger(__name__)
  # Set the log level to LOG_LEVEL
  logger.setLevel(LOG_LEVEL)
  # Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
  handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
  # Format each log message like this
  formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
  # Attach the formatter to the handler
  handler.setFormatter(formatter)
  # Attach the handler to the logger
  logger.addHandler(handler)

  # Make a class we can use to capture stdout and sterr in the log
  class MyLogger(object):
          def __init__(self, logger, level):
                  """Needs a logger and a logger level."""
                  self.logger = logger
                  self.level = level

          def write(self, message):
                  # Only log if there is a message (not just a new line)
                  if message.rstrip() != "":
                          self.logger.log(self.level, message.rstrip())

          def flush(self):
                  pass

  # Replace stdout with logging to file at INFO level
  sys.stdout = MyLogger(logger, logging.INFO)
  # Replace stderr with logging to file at ERROR level
  sys.stderr = MyLogger(logger, logging.ERROR)

  strip = apa102.APA102(args.led, 2)


  logger.info("try to connect to : " + str(args.ip) + " on port " + str(args.port));
  try:
    server = osc_server.ThreadingOSCUDPServer(
      (args.ip, args.port), dispatcher)
  except:
    server = osc_server.ThreadingOSCUDPServer(
      ("127.0.0.1", args.port), dispatcher)

  logger.info("Serving on " + str(server.server_address))
  logger.info("with %d LEDs", strip.numLEDs)
  server.serve_forever()


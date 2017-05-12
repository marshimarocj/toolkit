import json
import urllib
import argparse

from imposm.parser import OSMParser

'''func
'''
class RoadExtractor(object):
  roads = dict()
  crossings = dict()
  points = dict()

  def ways(self, ways):
    for osmid, tags, refs in ways:
      if 'highway' in tags:
        if 'crossing' in tags:
          if tags['crossing'] == 'zebra':
            self.crossings[osmid] = {'tags': tags, 'refs': refs}
        else:
          self.roads[osmid] = {'tags': tags, 'refs': refs}
        for ref in refs:
          self.points[ref] = None

  def nodes(self, nodes):
    for osmid, tags, coord in nodes:
      if osmid in self.points:
        self.points[osmid] = coord

  def coords(self, coords):
    for osmid, lng, lat in coords:
      if osmid in self.points:
        self.points[osmid] = (lng, lat)


class BuildingExtractor(object):
  buildings = dict()
  points = dict()

  def ways(self, ways):
    for osmid, tags, refs in ways:
      if 'building' in tags:
        self.buildings[osmid] = {'tags': tags, 'refs': refs}
        for ref in refs:
          self.points[ref] = None

  def nodes(self, nodes):
    for osmid, tags, coord in nodes:
      if osmid in self.points:
        self.points[osmid] = coord

  def coords(self, coords):
    for osmid, lat, lng in coords:
      if osmid in self.points:
        self.points[osmid] = (lat, lng)


def downloadOSM(minLongitude, maxLongitude, minLatitude, maxLatitude, mapfile):
  api = 'http://api.openstreetmap.org/api/0.6/map?bbox='

  url = '%s%s,%s,%s,%s'%(api, minLongitude, minLatitude, maxLongitude, maxLatitude)
  print url
  urllib.urlretrieve(url, mapfile)
  print mapfile


def parseRoad(mapfile, roadfile, concurrency=4):
  roadExtractor = RoadExtractor()
  p = OSMParser(concurrency=concurrency,
    ways_callback=roadExtractor.ways)
  p.parse(mapfile)

  p = OSMParser(concurrency=concurrency,
    nodes_callback=roadExtractor.nodes,
    coords_callback=roadExtractor.coords)
  p.parse(mapfile)

  roads = roadExtractor.roads
  points = roadExtractor.points

  roadName2segments = dict()
  for key in roads:
    road = roads[key]
    if 'name' not in road['tags'] and 'name:en' not in road['tags']: continue
    if 'name' in road['tags']:
      roadName = road['tags']['name']
    if 'name:en' in road['tags']:
      roadName = road['tags']['name:en']

    pointIds = road['refs']
    segment = []
    for pointId in pointIds:
      segment.append(points[pointId])
    if roadName not in roadName2segments: roadName2segments[roadName] = []
    roadName2segments[roadName].append(segment)

  with open(roadfile, 'w') as fout:
    json.dump(roadName2segments, fout)


def parseBuilding(mapfile, buildingfile, concurrency=4):
  buildingExtractor = BuildingExtractor()
  p = OSMParser(concurrency=concurrency,
    ways_callback=buildingExtractor.ways)
  p.parse(mapfile)
  p = OSMParser(concurrency=concurrency,
    nodes_callback=buildingExtractor.nodes,
    coords_callback=buildingExtractor.coords)
  p.parse(mapfile)

  with open(buildingfile, 'w') as fout:
    out = {
      'buildings': buildingExtractor.buildings,
      'points': buildingExtractor.points
    }
    json.dump(out, fout)


def buildParser():
  parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

  parser.add_argument('mapfile', help='osm format mapfile')
  parser.add_argument('prefix', help='prefix for the parsed road and building file')
  parser.add_argument('point1', help='point1 in lat,lng format')
  parser.add_argument('point2', help='point2 in lat,lng format')
  parser.add_argument('--concurrency', default=4, type=int,
    help='thread number in parsing osm mapfile')
  parser.add_argument('--parse_road', help='parse road?', action='store_true')
  parser.add_argument('--parse_building', help='parse building?', action='store_true')

  return parser


if __name__ == '__main__':
  parser = buildParser()
  args = parser.parse_args()

  point1 = [float(d) for d in args.point1.split(',')]
  point2 = [float(d) for d in args.point2.split(',')]
  minLatitude = min(point1[0], point2[0])
  maxLatitude = max(point1[0], point2[0])
  minLongitude = min(point1[1], point2[1])
  maxLongitude = max(point1[1], point2[1])

  downloadOSM(minLongitude, maxLongitude, 
    minLatitude, maxLatitude, args.mapfile)
  if args.parse_road:
    road_file = args.prefix + '.road.json'
    parseRoad(args.mapfile, road_file, concurrency=args.concurrency)
  if args.parse_building:
    building_file = args.prefix + '.building.json'
    parseBuilding(args.mapfile, building_file, concurrency=args.concurrency)

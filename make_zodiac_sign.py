import numpy
from PIL import Image, ImageDraw, ImageFilter
from select_stars_by_qa import select_stars_by_qa
import math

def make_zodiac_sign(image:Image, placement_angle, maximum_mag, blur_radius = 30, rate_of_using = 10000):
	blured_image = image.filter(ImageFilter.GaussianBlur(blur_radius))

	horizontal_offset = int(round(image.size[0] / 2))#天体と絵のスケール
	vertical_offset = int(round(image.size[1] / 2))#同上
	def trans_from_surface_to_image(m, n):
		new_m = m + horizontal_offset
		new_n = n + vertical_offset
		if 0 > new_m or 0 > new_n:
			return None
		if image.size[0] <= new_n or image.size[1] <= new_m:
			return None
		return new_m, new_n
	
	x, y, z = placement_angle
	radian_around_y = math.acos(z / math.sqrt(x ** 2 + z ** 2)) * (-1. if 0. < x else 1.)
	sin_around_y = math.sin(radian_around_y)
	cos_around_y = math.cos(radian_around_y)
	z = -x * sin_around_y + z * cos_around_y
	radian_around_x = math.acos(z / math.sqrt(z ** 2 + y ** 2)) * (-1. if 0. > y else 1.)
	sin_around_x = math.sin(radian_around_x)
	cos_around_x = math.cos(radian_around_x)
	def reverse_by_coordinate(x, y, z):
		#y 軸まわりの回転
		new_x = x * cos_around_y + z * sin_around_y
		new_z = -x * sin_around_y + z * cos_around_y
		#x 軸周りの回転
		new_y = y * cos_around_x - new_z * sin_around_x
		new_z = y * sin_around_x + new_z * cos_around_x
		return new_x, new_y, new_z

	candidate_list = []
	array_of_blured = numpy.array(blured_image)
	# with open("a.txt", "w") as file:
	# 	file.write(str(array_of_blured))
	import json
	with open('stars.json', 'r') as file:
		star_list = json.load(file)
	for star in star_list:
		if maximum_mag < star['mag']:
			continue
		x, y, z = reverse_by_coordinate(star['x'], star['y'], star['z'])
		if 0. > z:#視線方向に合わせて除外
			continue
		place_in_image = trans_from_surface_to_image(int(round(y)), int(round(x)))#視線方向に合わせて変更
		if None is place_in_image:
			continue
		candidate_list.append((star, array_of_blured[place_in_image[0], place_in_image[1], 3]))
	number_of_opaque = int(numpy.count_nonzero(numpy.array(image)[:, :, 3]))
	# chosen_star_list = choice_star_of_zodiac_dummy(candidate_list, int(round(numpy.count_nonzero(numpy.array(image)[:, :, 3]) / rate_of_using)))#qa 方式に差し替え
	chosen_star_list = select_stars_by_qa(
		sorted([star for star, _ in candidate_list], key=lambda x:x["mag"])[:15],
		qa_args={
			"lagrange_multiplier": 10,
			"token": "DEV-58f167ae5204fca8b0820e2bf71bf0613374fbef",
			"num_reads": 1000,
		},
		n_opaque=number_of_opaque,
		n_pixel=rate_of_using,
	)

	def trans_to_image(star):
		x, y, _ = reverse_by_coordinate(star['x'], star['y'], star['z'])
		return trans_from_surface_to_image(int(round(y)), int(round(x)))
	connection_list = connect_star_dummy(chosen_star_list, array_of_blured, trans_to_image)
	print(connection_list)
	return connection_list

def connect_star_dummy(star_list, array_of_image, trans_function):
	data_list = [(star['id'], trans_function(star)) for star in star_list]
	distance_list = sorted([((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2, (id1, id2), (coord1, coord2)) for id1, coord1 in data_list for id2, coord2 in data_list if id1 != id2], key=lambda x:x[0])
	def check_usable(coord1, coord2):
		target_matrix = array_of_image[coord1[0]:coord2[0], coord1[1]:coord2[1], 3]
		return len(target_matrix) == numpy.count_nonzero(target_matrix)
	group_list = [[id] for id, _ in data_list]
	def find_group(id):
		for index in range(len(group_list)):
			if id in group_list[index]:
				return index
	connection_list = []
	for _, (id1, id2), (coord1, coord2) in distance_list:
		index1 = find_group(id1)
		index2 = find_group(id2)
		if index1 == index2:
			continue
		if not check_usable(coord1, coord2):
			continue
		connection_list.append((id1, id2))
		group_list[index1] += group_list[index2]
		group_list.pop(index2)
		if 1 == len(group_list):
			break
	return connection_list
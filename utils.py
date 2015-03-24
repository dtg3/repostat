
from datetime import datetime, timedelta

def normalize_datetime(dateStrWithOffset):

		# first get the date without the offset (e.g., "+0200")
		date = datetime.strptime(dateStrWithOffset[:19], "%Y-%m-%d %H:%M:%S")

		# keey the offset, and grab the hours and minutes from it
		offset = dateStrWithOffset[20:]
		hours_off = int(offset[1:3])
		minutes_off = int(offset[3:])

		# provided time is ahead of UTC by some offset
		if offset[0] == '+':
			date = date - timedelta(hours=hours_off, minutes=minutes_off)

		# provided time is behind UTC by some offset
		elif offset[0] == '-':
			date = date + timedelta(hours=hours_off, minutes=minutes_off)

		return date

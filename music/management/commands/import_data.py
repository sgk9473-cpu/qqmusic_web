import os

from django.core.management.base import BaseCommand
from music.models import Singer, Song


class Command(BaseCommand):
    help = "导入 QQ 音乐爬虫数据"

    def handle(self, *args, **options):

        # =========================
        # 基础路径
        # =========================
        singer_data_dir = "singer_data"
        song_data_dir = "song_data"

        singer_image_dir = "singer_images"
        song_image_dir = "song_images"

        # =========================
        # 统计数量
        # =========================
        singer_count = 0
        song_count = 0

        # =========================
        # 导入歌手
        # =========================
        if not os.path.exists(singer_data_dir):
            self.stdout.write(
                self.style.ERROR(
                    f"找不到文件夹：{singer_data_dir}"
                )
            )
            return

        for filename in os.listdir(singer_data_dir):

            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(
                singer_data_dir,
                filename
            )

            data = self.parse_singer_file(file_path)

            singer_name = data["name"].strip()

            if not singer_name:
                continue

            image_path = os.path.join(
                singer_image_dir,
                os.path.splitext(filename)[0] + ".jpg"
            )

            Singer.objects.update_or_create(
                name=singer_name,
                defaults={
                    "source_url": data["source_url"],
                    "image": image_path,
                    "song_count": data["song_count"],
                    "follower_count": data["follower_count"],
                    "description": data["description"],
                }
            )

            singer_count += 1

        # =========================
        # 导入歌曲
        # =========================
        if not os.path.exists(song_data_dir):
            self.stdout.write(
                self.style.ERROR(
                    f"找不到文件夹：{song_data_dir}"
                )
            )
            return

        for filename in os.listdir(song_data_dir):

            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(
                song_data_dir,
                filename
            )

            data = self.parse_song_file(file_path)

            song_name = data["name"].strip()
            singer_name = data["singer_name"].strip()

            if not song_name or not singer_name:
                continue

            singer = Singer.objects.filter(
                name=singer_name
            ).first()

            if singer is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"歌曲《{song_name}》找不到歌手：{singer_name}"
                    )
                )
                continue

            image_path = os.path.join(
                song_image_dir,
                os.path.splitext(filename)[0] + ".jpg"
            )

            Song.objects.update_or_create(
                name=song_name,
                singer=singer,
                defaults={
                    "source_url": data["source_url"],
                    "image": image_path,
                    "lyric": data["lyric"],
                }
            )

            song_count += 1

        # =========================
        # 输出结果
        # =========================
        self.stdout.write(
            self.style.SUCCESS(
                f"数据导入完成！"
                f"歌手：{singer_count}，"
                f"歌曲：{song_count}"
            )
        )

    # ==================================================
    # 读取歌手 TXT
    # ==================================================
    def parse_singer_file(self, file_path):

        result = {
            "name": "",
            "source_url": "",
            "image_url": "",
            "song_count": "",
            "follower_count": "",
            "description": "",
        }

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:
            lines = f.readlines()

        description_started = False
        description_lines = []

        for line in lines:

            line = line.rstrip("\n")

            if line.startswith("歌手名字："):
                result["name"] = line.replace(
                    "歌手名字：",
                    "",
                    1
                )

            elif line.startswith("歌手原始网站URL："):
                result["source_url"] = line.replace(
                    "歌手原始网站URL：",
                    "",
                    1
                )

            elif line.startswith("歌手图片URL："):
                result["image_url"] = line.replace(
                    "歌手图片URL：",
                    "",
                    1
                )

            elif line.startswith("歌手单曲数："):
                result["song_count"] = line.replace(
                    "歌手单曲数：",
                    "",
                    1
                )

            elif line.startswith("歌手关注数："):
                result["follower_count"] = line.replace(
                    "歌手关注数：",
                    "",
                    1
                )

            elif line.startswith("歌手简介："):
                description_started = True

                description_lines.append(
                    line.replace(
                        "歌手简介：",
                        "",
                        1
                    )
                )

            elif description_started:
                description_lines.append(line)

        result["description"] = "\n".join(
            description_lines
        ).strip()

        return result

    # ==================================================
    # 读取歌曲 TXT
    # ==================================================
    def parse_song_file(self, file_path):

        result = {
            "name": "",
            "singer_name": "",
            "source_url": "",
            "image_url": "",
            "lyric": "",
        }

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:
            lines = f.readlines()

        lyric_started = False
        lyric_lines = []

        for line in lines:

            line = line.rstrip("\n")

            if line.startswith("歌曲名："):
                result["name"] = line.replace(
                    "歌曲名：",
                    "",
                    1
                )

            elif line.startswith("歌手名："):
                result["singer_name"] = line.replace(
                    "歌手名：",
                    "",
                    1
                )

            elif line.startswith("歌曲原始网站URL："):
                result["source_url"] = line.replace(
                    "歌曲原始网站URL：",
                    "",
                    1
                )

            elif line.startswith("歌曲图片URL："):
                result["image_url"] = line.replace(
                    "歌曲图片URL：",
                    "",
                    1
                )

            elif line.startswith("歌词："):
                lyric_started = True
                
                first_lyric_line = line.replace(
                    "歌词：",
                    "",
                    1
                ).strip()
                
                if first_lyric_line:
                    lyric_lines.append(first_lyric_line)
                    
            elif lyric_started:
                
                if line.startswith("[ti:"):
                    continue

                if line.startswith("[ar:"):
                    continue

                if line.startswith("[al:"):
                    continue

                if line.startswith("[by:"):
                    continue

                if line.startswith("[offset:"):
                    continue
                
                lyric_lines.append(line)


        result["lyric"] = "\n".join(
            lyric_lines
        ).strip()

        return result
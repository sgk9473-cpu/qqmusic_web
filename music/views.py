import time

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q,Case,IntegerField,When,Value

from .models import Song, Singer, Comment

def follower_to_number(value):
    if not value:
        return 0
    
    value = value.strip()
    
    try:
        if value.endswith("亿"):
            return float(value[:-1])*100000000
        if value.endswith("万"):
            return float(value[:-1])*10000
        return float(value)
    except (ValueError, TypeError):
        return 0


def home(request):
    return render(request, 'music/home.html')

def song_list(request):
    songs = Song.objects.select_related("singer").order_by("name")

    paginator = Paginator(songs, 20)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=2,
        on_ends=1,
    )

    return render(
        request,
        "music/song_list.html",
        {
            "page_obj": page_obj,
            "page_range": page_range,
        }
    )
    
def song_detail(request, song_id):
    song = get_object_or_404(
        Song.objects.select_related("singer"),
        id=song_id
    )

    if not request.session.session_key:
        request.session.create()

    current_session_key = request.session.session_key

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_comment":
            content = request.POST.get("content", "").strip()

            if content:
                Comment.objects.create(
                    song=song,
                    content=content,
                    session_key=current_session_key
                )

        elif action == "delete_comment":
            comment_id = request.POST.get("comment_id")

            Comment.objects.filter(
                id=comment_id,
                song=song,
                session_key=current_session_key
            ).delete()

    comments = song.comments.order_by("-created_at")

    return render(
        request,
        "music/song_detail.html",
        {
            "song": song,
            "comments": comments,
            "current_session_key": current_session_key,
        }
    )
    
def singer_detail(request, singer_id):
    singer = get_object_or_404(Singer, id=singer_id)
    
    songs = singer.songs.order_by("name")
    
    return render(
        request,
        "music/singer_detail.html",
        {
            "singer": singer,
            "songs": songs
        }
    )
    
def singer_list(request):
    singers = list(Singer.objects.all())

    singers.sort(
        key=lambda singer: follower_to_number(
            singer.follower_count
        ),
        reverse=True
    )

    paginator = Paginator(singers, 20)

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=2,
        on_ends=1,
    )

    return render(
        request,
        "music/singer_list.html",
        {
            "page_obj": page_obj,
            "page_range": page_range,
        }
    )

def search(request):
    keyword = request.GET.get("keyword", "").strip()
    search_type = request.GET.get("type", "song")

    # 最多 20 个字符
    if len(keyword) > 20:
        keyword = keyword[:20]

    
    if not keyword:
        return render(
            request,
            "music/search_result.html",
            {
                "page_obj": None,
                "page_range": [],
                "keyword": "",
                "search_type": search_type,
                "result_count": 0,
                "search_time": 0,
                "empty_search": True,
            }
        )

    start_time = time.perf_counter()

    if search_type == "singer":

        results = (
            Singer.objects
            .filter(
                Q(name__icontains=keyword) |
                Q(description__icontains=keyword)
            )
            .annotate(
                relevance=Case(
                    # 歌手名完全匹配
                    When(
                        name__iexact=keyword,
                        then=Value(100)
                    ),

                    # 歌手名以关键词开头
                    When(
                        name__istartswith=keyword,
                        then=Value(80)
                    ),

                    # 歌手名包含关键词
                    When(
                        name__icontains=keyword,
                        then=Value(70)
                    ),

                    # 简介包含关键词
                    When(
                        description__icontains=keyword,
                        then=Value(30)
                    ),

                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("-relevance", "name")
        )

    else:

        results = (
            Song.objects
            .select_related("singer")
            .filter(
                Q(name__icontains=keyword) |
                Q(singer__name__icontains=keyword) |
                Q(lyric__icontains=keyword)
            )
            .annotate(
                relevance=Case(
                    # 歌曲名完全匹配
                    When(
                        name__iexact=keyword,
                        then=Value(100)
                    ),

                    # 歌曲名以关键词开头
                    When(
                        name__istartswith=keyword,
                        then=Value(90)
                    ),

                    # 歌曲名包含关键词
                    When(
                        name__icontains=keyword,
                        then=Value(80)
                    ),

                    # 歌手名完全匹配
                    When(
                        singer__name__iexact=keyword,
                        then=Value(70)
                    ),

                    # 歌手名包含关键词
                    When(
                        singer__name__icontains=keyword,
                        then=Value(60)
                    ),

                    # 歌词包含关键词
                    When(
                        lyric__icontains=keyword,
                        then=Value(30)
                    ),

                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("-relevance", "name")
        )

    result_count = results.count()

    end_time = time.perf_counter()

    search_time = end_time - start_time

    paginator = Paginator(results, 20)

    page_number = request.GET.get("page", 1)

    page_obj = paginator.get_page(page_number)
    
    page_range = paginator.get_elided_page_range(
        number=page_obj.number,
        on_each_side=2,
        on_ends=1,
    )

    return render(
        request,
        "music/search_result.html",
        {
            "page_obj": page_obj,
            "page_range": page_range,
            "keyword": keyword,
            "search_type": search_type,
            "result_count": result_count,
            "search_time": search_time,
        }
    )

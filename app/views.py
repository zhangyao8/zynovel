from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import HttpResponseRedirect
from app import dload
from app import models
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def index(request):
    return HttpResponse('ok')


@login_required
def manager(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        try:
            bookid = dload.gethtml(url)
            return HttpResponse('/book/{}/'.format(bookid))
            # return HttpResponseRedirect('/book/{}/'.format(bookid))
        except Exception as e:
            return HttpResponse('出现错误：{}'.format(e))

    if request.method == 'GET':
        return render(request, 'manager.html')


@login_required
def search(request):
    if request.method == 'POST':
        bookname = request.POST.get('bookname')
        bookret = dload.searchbook(bookname)
        ret = str(bookret).replace('\n', '')
        return HttpResponse(ret)


@login_required
def bookshelf(request):
    shelfquery = models.Novel.objects.filter(status=1).values('id', 'name')
    return render(request, 'bookshelf.html', {'shelfquery': shelfquery})


@login_required
def book(request, bookid):
    bookdict = dload.bookdetail(bookid)
    return render(request, 'book.html', bookdict)


@login_required
def chapter(request, bookid, chapterid):
    textdict = dload.downloadone(bookid, chapterid)
    dload.readrecord(bookid, chapterid)
    return render(request, 'chapter.html', textdict)


@login_required
def cachechapter(request):
    if request.method == 'POST':
        bookid = request.POST.get('bookid')
        chapterid = request.POST.get('chapterid', None)
        dload.cachedownload(bookid, chapterid)
        return HttpResponse('缓存完成')


@login_required
def downbook(request, bookid, chapterid):
    bookname = dload.downloadepub(bookid, chapterid)
    return HttpResponseRedirect('http://www.zyops.com/zynovel/{0}/{0}.epub'.format(bookname))

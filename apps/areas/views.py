from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from ltmall.utils.response_code import RETCODE
from areas.models import Area
from django_redis import get_redis_connection
from django.core.cache import cache
from ltmall.settings import const
import logging

logger = logging.getLogger('django')


class AreasView(View):
    """省市区三级联动"""

    def get(self, request):
        # 通过URL获取area_id
        area_id = request.GET.get('area_id')
        # 判断当前是要查询省份还是市区数据
        if area_id:
            # 获取缓存
            sub_data = cache.get('sub_data_' + area_id)
            if not sub_data:
                # 获取市区数据
                try:
                    province = Area.objects.get(id=area_id)
                    citys = province.subs.all()
                    # citys = Area.objects.filter(parent_id=area_id)
                    """
                    {
                      "code":"0",
                      "errmsg":"OK",
                      "sub_data":{
                          "id":130000,
                          "name":"河北省",
                          "subs":[
                              {
                                  "id":130100,
                                  "name":"石家庄市"
                              },
                              ......
                          ]
                      }
                    }
                    """
                    subs_list = []
                    for city in citys:
                        city = {
                            "id": city.id,
                            "name": city.name
                        }
                        subs_list.append(city)

                    sub_data = {
                        "id": area_id,
                        "name": province.name,
                        "subs": subs_list
                    }
                    # 设置缓存
                    cache.set('sub_data_' + area_id, sub_data, const.AREAS_CACHE_EXPIRES)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '区域查询失败'})
            # 响应结果
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "sub_data": sub_data})

        else:
            # 获取缓存
            province_list = cache.get('province_list')
            if not province_list:
                # id为空说明是省
                try:
                    province_model_list = Area.objects.filter(parent__isnull=True)
                    province_list = []
                    for province in province_model_list:
                        province_dict = {
                            "id": province.id,
                            "name": province.name
                        }
                        province_list.append(province_dict)
                    # 设置缓存
                    cache.set('province', province_list, const.AREAS_CACHE_EXPIRES)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份查询失败'})

            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "province_list": province_list})

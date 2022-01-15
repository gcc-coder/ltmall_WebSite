let vm = new Vue({
    el: "#register_app",
    // 修改Vue变量的读取语法
    delimiters: ['[[', ']]'],
    data: {
        // others
        uuid: '',
        image_code_url: '',
        sms_code_url: '',

        // v-model
        username: '',
        password: '',
        password2: '',
        mobile: '',
        allow: '',
        image_code: '',
        sms_code: '',
        sms_code_tip: "获取短信验证码",
        send_flag: false,   // 定义flag，实现前端避免频繁发送短信验证码的逻辑

        // v-show
        error_username: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,

        // error_message
        error_username_msg: '',
        error_password_msg: '',
        error_password2_msg: '',
        error_mobile_msg: '',
        error_allow_msg: '',
        error_image_code_msg: '',
        error_sms_code_msg: '',
    },
    // 页面加载完成之后，才会被调用的方法
    mounted(){
        // 展示图形验证码
        this.generate_image_code()
    },
    methods: {
        // 获取短信验证码
        send_sms_code() {
            // alert(1);
            if (this.send_flag == true){
                // 避免频繁发送短信验证码
                return ;
            }
            this.send_flag = true   // 第二次点击
            // 先校验手机号和图形验证码是否符合要求
            this.check_mobile();
            this.check_image_code();
            if (this.error_mobile == true || this.error_image_code == true){
                console.log('手机号或图形验证码不正确')
                // this.send_flag = false
                return;
            };
            // sms_codes/(?P<mobile>1[3-9]\d{9})/?image_code=xxxx&uuid=xxxx
            let url = "/sms_codes/" + this.mobile + "/?image_code=" + this.image_code + "&uuid=" + this.uuid;
            // alert(url)
            axios.get(url, {
                responseType: 'json'
            })
            .then(response => {
                let num = 60
                if (response.data.code == '0'){
                    // 定时器
                    let t = setInterval(()=>{
                        if (num == 1){
                            // 定时器停止的逻辑
                            clearInterval(t);
                            this.sms_code_tip = '获取短信验证码';
                            this.generate_image_code(); // 重新生成图形验证码
                            this.send_flag = false
                        }else {
                            num -= 1;
                            this.sms_code_tip = num + '秒后重试'
                        }
                    }, 1000)
                }else{
                    if (response.data.code == '4001'){
                        // alert(4001)
                        // 图形验证码输入有误
                        this.error_image_code_msg = response.data.errmsg;
                        this.error_image_code = true;
                        this.send_flag = true;
                    }
                    this.send_flag = false
                }
            })
            .catch(error => {
                console.log(error.response)
                this.send_flag = false
            })
        },
        // 校验短信验证码
        check_sms_code(){
            if (this.sms_code.length != 6){
                this.error_sms_code = true;
                this.error_sms_code_msg = "请填写6位短信验证码"
            }else {
                this.error_sms_code = false;
            }
        },
        // 生成图形验证码
        generate_image_code(){
            // 生成UUID。函数generateUUID(): 封装在common.js文件中，需提前引入
            this.uuid = generateUUID();
            this.image_code_url = '/image_codes/'+ this.uuid +'/';
        },
        // 校验图形验证码
        check_image_code(){
            if (this.image_code.length != 4){
                // alert(this.image_code)
                this.error_image_code = true;
                this.error_image_code_msg = "请填写4位图形验证码"
            }else {
                this.error_image_code = false;
            }
        },
        // 检验用户名
        check_username(){
            let re = /^[a-zA-Z0-9_-]{4,20}$/;
            if (re.test(this.username)){
                // 正则匹配成功，则不展示错误信息
                this.error_username = false
            } else {
                // 正则匹配成功，显示错误信息
                this.error_username = true
                this.error_username_msg = "请输入4-20个字符的用户"
            };
            // 若符合用户名规则， 则验证是否已存在
            if (this.error_username == false){
                let url = '/users/username/'+ this.username +'/count/';
                // axios.get(参数url, 请求头->字典格式)
                axios.get(url, {
                    responseType: 'json'
                })
                // 请求成功的处理逻辑  箭头函数response => 等同于 function(response)
                .then(response => {
                    // console.log(response.data);
                    if (response.data.count == 1){
                        // 用户名已经存在
                        this.error_username_msg = '用户名已经存在';
                        this.error_username = true
                    }else {
                        this.error_username = false
                    }
                })
                // 请求失败
                .catch(error => {
                    console.log(error.response)
                })
            }
        },
        check_password(){
            let re = /^[a-zA-Z0-9_-]{6,10}$/;
            if (re.test(this.password)){
                this.error_password = false
            } else {
                this.error_password = true
                this.error_password_msg = "请输入6-10位的密码"
            }
        },
        check_password2(){
            if (this.password != this.password2) {
                this.error_password2 = true;
                this.error_password2_msg = "两次密码不一致"

            } else {
                this.error_password2 = false;
            }
        },
        check_mobile(){
            let re = /^1[3-9]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_msg = '您输入的手机号格式不正确';
                this.error_mobile = true;
            };
            // 若符合用户名规则， 则验证是否已存在
            if (this.error_mobile == false){
                let url = '/users/mobile/'+ this.mobile +'/count/';
                // axios.get(url, 请求头-字典格式)
                axios.get(url, {
                    responseType: 'json'
                })
                    // 请求成功的处理逻辑  箭头函数response => 等同于 function(response)
                    .then(response => {
                        // console.log(response.data);
                        if (response.data.count == 1){
                            // 手机号已经存在
                            this.error_mobile_msg = '该手机号已经注册';
                            this.error_mobile = true
                        }else {
                            this.error_mobile = false
                        }
                    })
                    // 请求失败
                    .catch(error => {
                        console.log(error.response)
                    })
            }

        },
        check_allow(){
            if (!this.allow) {
                this.error_allow = true;
                this.error_allow_msg = '请勾选用户协议';
            } else {
                this.error_allow = false;
            }
        },
        on_submit(){
            // 校验表单提交的数据结果
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_image_code();
            this.check_sms_code();
            this.check_allow();

            // 校验错误数据都为true时的处理逻辑
            if (this.error_username == true || this.error_password == true || this.error_password2 == true || this.error_mobile == true || this.error_allow == true || this.error_image_code == true || this.error_sms_code == true) {
                // 不满足登录条件：禁用表单提交
				window.event.returnValue = false
            }

        }
    }
})


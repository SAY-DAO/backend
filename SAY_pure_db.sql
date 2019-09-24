PGDMP     	                    w           SAY    11.4 (Debian 11.4-1.pgdg90+1)    11.4 c    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                       false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                       false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                       false            �           1262    17008    SAY    DATABASE     u   CREATE DATABASE "SAY" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';
    DROP DATABASE "SAY";
             postgres    false            �            1259    19157    activity    TABLE     �   CREATE TABLE public.activity (
    "activityCode" integer NOT NULL,
    id integer NOT NULL,
    id_social_worker integer NOT NULL
);
    DROP TABLE public.activity;
       public         postgres    false            �            1259    19155    activity_id_seq    SEQUENCE     �   CREATE SEQUENCE public.activity_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.activity_id_seq;
       public       postgres    false    197            �           0    0    activity_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.activity_id_seq OWNED BY public.activity.id;
            public       postgres    false    196            �            1259    19211    child    TABLE     �  CREATE TABLE public.child (
    "phoneNumber" character varying NOT NULL,
    nationality character varying,
    "avatarUrl" character varying NOT NULL,
    id integer NOT NULL,
    "housingStatus" character varying,
    "firstName" character varying,
    "lastName" character varying,
    "familyCount" integer,
    education character varying,
    "createdAt" date NOT NULL,
    "birthPlace" character varying,
    address text,
    bio text NOT NULL,
    "voiceUrl" character varying NOT NULL,
    id_ngo integer NOT NULL,
    id_social_worker integer NOT NULL,
    "confirmUser" integer,
    "confirmDate" date,
    "sayName" character varying NOT NULL,
    "generatedCode" character varying NOT NULL,
    city integer NOT NULL,
    country integer NOT NULL,
    gender boolean NOT NULL,
    "birthDate" date,
    status integer,
    "doneNeedCount" integer DEFAULT 0 NOT NULL,
    "spentCredit" integer DEFAULT 0 NOT NULL,
    "isDeleted" boolean DEFAULT false NOT NULL,
    "isConfirmed" boolean DEFAULT false NOT NULL,
    "bioSummary" text NOT NULL,
    "sayFamilyCount" integer DEFAULT 0 NOT NULL,
    "lastUpdate" date NOT NULL,
    "isMigrated" boolean DEFAULT false NOT NULL,
    "migratedId" integer,
    "migrateDate" date
);
    DROP TABLE public.child;
       public         postgres    false            �            1259    19209    child_id_seq    SEQUENCE     �   CREATE SEQUENCE public.child_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.child_id_seq;
       public       postgres    false    205            �           0    0    child_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.child_id_seq OWNED BY public.child.id;
            public       postgres    false    204            �            1259    19274 
   child_need    TABLE     �   CREATE TABLE public.child_need (
    id_need integer NOT NULL,
    id integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_child integer NOT NULL
);
    DROP TABLE public.child_need;
       public         postgres    false            �            1259    19272    child_need_id_seq    SEQUENCE     �   CREATE SEQUENCE public.child_need_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.child_need_id_seq;
       public       postgres    false    213            �           0    0    child_need_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.child_need_id_seq OWNED BY public.child_need.id;
            public       postgres    false    212            �            1259    19245    family    TABLE     y   CREATE TABLE public.family (
    id integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_child integer NOT NULL
);
    DROP TABLE public.family;
       public         postgres    false            �            1259    19243    family_id_seq    SEQUENCE     �   CREATE SEQUENCE public.family_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.family_id_seq;
       public       postgres    false    209            �           0    0    family_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.family_id_seq OWNED BY public.family.id;
            public       postgres    false    208            �            1259    19258    need    TABLE     �  CREATE TABLE public.need (
    id integer NOT NULL,
    name character varying NOT NULL,
    "imageUrl" character varying NOT NULL,
    category integer NOT NULL,
    description text NOT NULL,
    cost integer NOT NULL,
    "affiliateLinkUrl" character varying,
    "createdAt" date NOT NULL,
    receipts character varying,
    progress integer DEFAULT 0 NOT NULL,
    paid integer DEFAULT 0 NOT NULL,
    "confirmDate" date,
    "confirmUser" integer,
    "isDone" boolean DEFAULT false NOT NULL,
    "isDeleted" boolean DEFAULT false NOT NULL,
    "isConfirmed" boolean DEFAULT false NOT NULL,
    type integer NOT NULL,
    "descriptionSummary" text NOT NULL,
    "lastUpdate" date NOT NULL,
    "isUrgent" boolean NOT NULL
);
    DROP TABLE public.need;
       public         postgres    false            �            1259    19292    need_family    TABLE     �   CREATE TABLE public.need_family (
    id integer NOT NULL,
    id_family integer NOT NULL,
    id_user integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_need integer NOT NULL
);
    DROP TABLE public.need_family;
       public         postgres    false            �            1259    19290    need_family_id_seq    SEQUENCE     �   CREATE SEQUENCE public.need_family_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.need_family_id_seq;
       public       postgres    false    215            �           0    0    need_family_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.need_family_id_seq OWNED BY public.need_family.id;
            public       postgres    false    214            �            1259    19256    need_id_seq    SEQUENCE     �   CREATE SEQUENCE public.need_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 "   DROP SEQUENCE public.need_id_seq;
       public       postgres    false    211            �           0    0    need_id_seq    SEQUENCE OWNED BY     ;   ALTER SEQUENCE public.need_id_seq OWNED BY public.need.id;
            public       postgres    false    210            �            1259    19165    ngo    TABLE     $  CREATE TABLE public.ngo (
    id integer NOT NULL,
    "coordinatorId" integer NOT NULL,
    name character varying NOT NULL,
    "postalAddress" text NOT NULL,
    "emailAddress" character varying NOT NULL,
    "phoneNumber" character varying NOT NULL,
    "logoUrl" character varying NOT NULL,
    balance integer DEFAULT 0 NOT NULL,
    "socialWorkerCount" integer DEFAULT 0 NOT NULL,
    "childrenCount" integer DEFAULT 0 NOT NULL,
    "registerDate" date NOT NULL,
    "lastUpdateDate" date NOT NULL,
    "isActive" boolean DEFAULT true NOT NULL,
    "isDeleted" boolean DEFAULT false NOT NULL,
    city integer NOT NULL,
    country integer NOT NULL,
    "currentSocialWorkerCount" integer DEFAULT 0 NOT NULL,
    "currentChildrenCount" integer DEFAULT 0 NOT NULL,
    website character varying
);
    DROP TABLE public.ngo;
       public         postgres    false            �            1259    19163 
   ngo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.ngo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 !   DROP SEQUENCE public.ngo_id_seq;
       public       postgres    false    199            �           0    0 
   ngo_id_seq    SEQUENCE OWNED BY     9   ALTER SEQUENCE public.ngo_id_seq OWNED BY public.ngo.id;
            public       postgres    false    198            �            1259    19315    payment    TABLE     �   CREATE TABLE public.payment (
    id integer NOT NULL,
    id_user integer NOT NULL,
    amount integer NOT NULL,
    "createdAt" date NOT NULL,
    id_need integer NOT NULL
);
    DROP TABLE public.payment;
       public         postgres    false            �            1259    19313    payment_id_seq    SEQUENCE     �   CREATE SEQUENCE public.payment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.payment_id_seq;
       public       postgres    false    217            �           0    0    payment_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.payment_id_seq OWNED BY public.payment.id;
            public       postgres    false    216            �            1259    19183    social_worker    TABLE     �  CREATE TABLE public.social_worker (
    id integer NOT NULL,
    "generatedCode" character varying NOT NULL,
    id_ngo integer NOT NULL,
    id_type integer NOT NULL,
    "firstName" character varying,
    "lastName" character varying NOT NULL,
    "userName" character varying NOT NULL,
    password character varying NOT NULL,
    "birthCertificateNumber" character varying,
    "idNumber" character varying NOT NULL,
    "idCardUrl" character varying,
    "passportNumber" character varying,
    "birthDate" date,
    "phoneNumber" character varying NOT NULL,
    "emergencyPhoneNumber" character varying NOT NULL,
    "emailAddress" character varying NOT NULL,
    "telegramId" character varying NOT NULL,
    "postalAddress" text,
    "avatarUrl" character varying NOT NULL,
    "childCount" integer DEFAULT 0 NOT NULL,
    "needCount" integer DEFAULT 0 NOT NULL,
    "bankAccountNumber" character varying,
    "bankAccountShebaNumber" character varying,
    "bankAccountCardNumber" character varying,
    "registerDate" date NOT NULL,
    "lastUpdateDate" date NOT NULL,
    "lastLoginDate" date NOT NULL,
    "lastLogoutDate" date,
    "passportUrl" character varying,
    "isActive" boolean DEFAULT true NOT NULL,
    "isDeleted" boolean DEFAULT false NOT NULL,
    gender boolean NOT NULL,
    city integer,
    country integer,
    "currentChildCount" integer DEFAULT 0 NOT NULL,
    "currentNeedCount" integer DEFAULT 0 NOT NULL
);
 !   DROP TABLE public.social_worker;
       public         postgres    false            �            1259    19181    social_worker_id_seq    SEQUENCE     �   CREATE SEQUENCE public.social_worker_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.social_worker_id_seq;
       public       postgres    false    201            �           0    0    social_worker_id_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.social_worker_id_seq OWNED BY public.social_worker.id;
            public       postgres    false    200            �            1259    19200    social_worker_type    TABLE     �   CREATE TABLE public.social_worker_type (
    id integer NOT NULL,
    name character varying NOT NULL,
    privilege integer NOT NULL
);
 &   DROP TABLE public.social_worker_type;
       public         postgres    false            �            1259    19198    social_worker_type_id_seq    SEQUENCE     �   CREATE SEQUENCE public.social_worker_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.social_worker_type_id_seq;
       public       postgres    false    203            �           0    0    social_worker_type_id_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.social_worker_type_id_seq OWNED BY public.social_worker_type.id;
            public       postgres    false    202            �            1259    19228    user    TABLE        CREATE TABLE public."user" (
    "firstName" character varying NOT NULL,
    "lastName" character varying NOT NULL,
    credit integer DEFAULT 0 NOT NULL,
    "avatarUrl" character varying,
    "phoneNumber" character varying NOT NULL,
    "userName" character varying,
    "createdAt" date NOT NULL,
    "lastUpdate" date NOT NULL,
    "birthDate" date,
    "birthPlace" character varying,
    "flagUrl" character varying,
    "emailAddress" character varying,
    gender boolean,
    "isDeleted" boolean DEFAULT false NOT NULL,
    city integer NOT NULL,
    country integer NOT NULL,
    "lastLogin" date NOT NULL,
    password character varying,
    "spentCredit" integer DEFAULT 0 NOT NULL,
    "doneNeedCount" integer DEFAULT 0 NOT NULL,
    id integer NOT NULL,
    token character varying
);
    DROP TABLE public."user";
       public         postgres    false            �            1259    19333    user_family    TABLE     �   CREATE TABLE public.user_family (
    id integer NOT NULL,
    id_family integer NOT NULL,
    "userRole" integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_user integer NOT NULL
);
    DROP TABLE public.user_family;
       public         postgres    false            �            1259    19331    user_family_id_seq    SEQUENCE     �   CREATE SEQUENCE public.user_family_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 )   DROP SEQUENCE public.user_family_id_seq;
       public       postgres    false    219            �           0    0    user_family_id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public.user_family_id_seq OWNED BY public.user_family.id;
            public       postgres    false    218            �            1259    19226    user_id_seq    SEQUENCE     �   CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 "   DROP SEQUENCE public.user_id_seq;
       public       postgres    false    207            �           0    0    user_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;
            public       postgres    false    206            �
           2604    19160    activity id    DEFAULT     j   ALTER TABLE ONLY public.activity ALTER COLUMN id SET DEFAULT nextval('public.activity_id_seq'::regclass);
 :   ALTER TABLE public.activity ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    197    196    197                       2604    19214    child id    DEFAULT     d   ALTER TABLE ONLY public.child ALTER COLUMN id SET DEFAULT nextval('public.child_id_seq'::regclass);
 7   ALTER TABLE public.child ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    205    204    205                        2604    19277    child_need id    DEFAULT     n   ALTER TABLE ONLY public.child_need ALTER COLUMN id SET DEFAULT nextval('public.child_need_id_seq'::regclass);
 <   ALTER TABLE public.child_need ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    213    212    213                       2604    19248 	   family id    DEFAULT     f   ALTER TABLE ONLY public.family ALTER COLUMN id SET DEFAULT nextval('public.family_id_seq'::regclass);
 8   ALTER TABLE public.family ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    209    208    209                       2604    19261    need id    DEFAULT     b   ALTER TABLE ONLY public.need ALTER COLUMN id SET DEFAULT nextval('public.need_id_seq'::regclass);
 6   ALTER TABLE public.need ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    210    211    211            !           2604    19295    need_family id    DEFAULT     p   ALTER TABLE ONLY public.need_family ALTER COLUMN id SET DEFAULT nextval('public.need_family_id_seq'::regclass);
 =   ALTER TABLE public.need_family ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    214    215    215            �
           2604    19168    ngo id    DEFAULT     `   ALTER TABLE ONLY public.ngo ALTER COLUMN id SET DEFAULT nextval('public.ngo_id_seq'::regclass);
 5   ALTER TABLE public.ngo ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    199    198    199            "           2604    19318 
   payment id    DEFAULT     h   ALTER TABLE ONLY public.payment ALTER COLUMN id SET DEFAULT nextval('public.payment_id_seq'::regclass);
 9   ALTER TABLE public.payment ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    217    216    217                       2604    19186    social_worker id    DEFAULT     t   ALTER TABLE ONLY public.social_worker ALTER COLUMN id SET DEFAULT nextval('public.social_worker_id_seq'::regclass);
 ?   ALTER TABLE public.social_worker ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    201    200    201                       2604    19203    social_worker_type id    DEFAULT     ~   ALTER TABLE ONLY public.social_worker_type ALTER COLUMN id SET DEFAULT nextval('public.social_worker_type_id_seq'::regclass);
 D   ALTER TABLE public.social_worker_type ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    202    203    203                       2604    19235    user id    DEFAULT     d   ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);
 8   ALTER TABLE public."user" ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    207    206    207            #           2604    19336    user_family id    DEFAULT     p   ALTER TABLE ONLY public.user_family ALTER COLUMN id SET DEFAULT nextval('public.user_family_id_seq'::regclass);
 =   ALTER TABLE public.user_family ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    219    218    219            �          0    19157    activity 
   TABLE DATA               H   COPY public.activity ("activityCode", id, id_social_worker) FROM stdin;
    public       postgres    false    197   1�       �          0    19211    child 
   TABLE DATA               �  COPY public.child ("phoneNumber", nationality, "avatarUrl", id, "housingStatus", "firstName", "lastName", "familyCount", education, "createdAt", "birthPlace", address, bio, "voiceUrl", id_ngo, id_social_worker, "confirmUser", "confirmDate", "sayName", "generatedCode", city, country, gender, "birthDate", status, "doneNeedCount", "spentCredit", "isDeleted", "isConfirmed", "bioSummary", "sayFamilyCount", "lastUpdate", "isMigrated", "migratedId", "migrateDate") FROM stdin;
    public       postgres    false    205   N�       �          0    19274 
   child_need 
   TABLE DATA               H   COPY public.child_need (id_need, id, "isDeleted", id_child) FROM stdin;
    public       postgres    false    213   k�       �          0    19245    family 
   TABLE DATA               ;   COPY public.family (id, "isDeleted", id_child) FROM stdin;
    public       postgres    false    209   ��       �          0    19258    need 
   TABLE DATA                 COPY public.need (id, name, "imageUrl", category, description, cost, "affiliateLinkUrl", "createdAt", receipts, progress, paid, "confirmDate", "confirmUser", "isDone", "isDeleted", "isConfirmed", type, "descriptionSummary", "lastUpdate", "isUrgent") FROM stdin;
    public       postgres    false    211   ��       �          0    19292    need_family 
   TABLE DATA               S   COPY public.need_family (id, id_family, id_user, "isDeleted", id_need) FROM stdin;
    public       postgres    false    215          �          0    19165    ngo 
   TABLE DATA               )  COPY public.ngo (id, "coordinatorId", name, "postalAddress", "emailAddress", "phoneNumber", "logoUrl", balance, "socialWorkerCount", "childrenCount", "registerDate", "lastUpdateDate", "isActive", "isDeleted", city, country, "currentSocialWorkerCount", "currentChildrenCount", website) FROM stdin;
    public       postgres    false    199   ߂       �          0    19315    payment 
   TABLE DATA               L   COPY public.payment (id, id_user, amount, "createdAt", id_need) FROM stdin;
    public       postgres    false    217   ��       �          0    19183    social_worker 
   TABLE DATA               A  COPY public.social_worker (id, "generatedCode", id_ngo, id_type, "firstName", "lastName", "userName", password, "birthCertificateNumber", "idNumber", "idCardUrl", "passportNumber", "birthDate", "phoneNumber", "emergencyPhoneNumber", "emailAddress", "telegramId", "postalAddress", "avatarUrl", "childCount", "needCount", "bankAccountNumber", "bankAccountShebaNumber", "bankAccountCardNumber", "registerDate", "lastUpdateDate", "lastLoginDate", "lastLogoutDate", "passportUrl", "isActive", "isDeleted", gender, city, country, "currentChildCount", "currentNeedCount") FROM stdin;
    public       postgres    false    201   �       �          0    19200    social_worker_type 
   TABLE DATA               A   COPY public.social_worker_type (id, name, privilege) FROM stdin;
    public       postgres    false    203   6�       �          0    19228    user 
   TABLE DATA                  COPY public."user" ("firstName", "lastName", credit, "avatarUrl", "phoneNumber", "userName", "createdAt", "lastUpdate", "birthDate", "birthPlace", "flagUrl", "emailAddress", gender, "isDeleted", city, country, "lastLogin", password, "spentCredit", "doneNeedCount", id, token) FROM stdin;
    public       postgres    false    207   S�       �          0    19333    user_family 
   TABLE DATA               V   COPY public.user_family (id, id_family, "userRole", "isDeleted", id_user) FROM stdin;
    public       postgres    false    219   p�       �           0    0    activity_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.activity_id_seq', 1, false);
            public       postgres    false    196            �           0    0    child_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.child_id_seq', 1, false);
            public       postgres    false    204            �           0    0    child_need_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.child_need_id_seq', 1, false);
            public       postgres    false    212            �           0    0    family_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.family_id_seq', 1, false);
            public       postgres    false    208            �           0    0    need_family_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.need_family_id_seq', 1, false);
            public       postgres    false    214            �           0    0    need_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.need_id_seq', 1, false);
            public       postgres    false    210            �           0    0 
   ngo_id_seq    SEQUENCE SET     9   SELECT pg_catalog.setval('public.ngo_id_seq', 1, false);
            public       postgres    false    198            �           0    0    payment_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.payment_id_seq', 1, false);
            public       postgres    false    216            �           0    0    social_worker_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.social_worker_id_seq', 1, false);
            public       postgres    false    200            �           0    0    social_worker_type_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.social_worker_type_id_seq', 1, false);
            public       postgres    false    202            �           0    0    user_family_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.user_family_id_seq', 1, false);
            public       postgres    false    218            �           0    0    user_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.user_id_seq', 1, false);
            public       postgres    false    206            %           2606    19162    activity activity_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.activity DROP CONSTRAINT activity_pkey;
       public         postgres    false    197            7           2606    19279    child_need child_need_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.child_need
    ADD CONSTRAINT child_need_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.child_need DROP CONSTRAINT child_need_pkey;
       public         postgres    false    213            -           2606    19225    child child_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.child
    ADD CONSTRAINT child_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.child DROP CONSTRAINT child_pkey;
       public         postgres    false    205            3           2606    19250    family family_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.family
    ADD CONSTRAINT family_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.family DROP CONSTRAINT family_pkey;
       public         postgres    false    209            9           2606    19297    need_family need_family_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.need_family
    ADD CONSTRAINT need_family_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.need_family DROP CONSTRAINT need_family_pkey;
       public         postgres    false    215            5           2606    19271    need need_pkey 
   CONSTRAINT     L   ALTER TABLE ONLY public.need
    ADD CONSTRAINT need_pkey PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.need DROP CONSTRAINT need_pkey;
       public         postgres    false    211            '           2606    19180    ngo ngo_pkey 
   CONSTRAINT     J   ALTER TABLE ONLY public.ngo
    ADD CONSTRAINT ngo_pkey PRIMARY KEY (id);
 6   ALTER TABLE ONLY public.ngo DROP CONSTRAINT ngo_pkey;
       public         postgres    false    199            ;           2606    19320    payment payment_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.payment DROP CONSTRAINT payment_pkey;
       public         postgres    false    217            )           2606    19197     social_worker social_worker_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.social_worker
    ADD CONSTRAINT social_worker_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.social_worker DROP CONSTRAINT social_worker_pkey;
       public         postgres    false    201            +           2606    19208 *   social_worker_type social_worker_type_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.social_worker_type
    ADD CONSTRAINT social_worker_type_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.social_worker_type DROP CONSTRAINT social_worker_type_pkey;
       public         postgres    false    203            /           2606    19242    user user_PhoneNumber_key 
   CONSTRAINT     a   ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "user_PhoneNumber_key" UNIQUE ("phoneNumber");
 G   ALTER TABLE ONLY public."user" DROP CONSTRAINT "user_PhoneNumber_key";
       public         postgres    false    207            =           2606    19338    user_family user_family_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.user_family
    ADD CONSTRAINT user_family_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.user_family DROP CONSTRAINT user_family_pkey;
       public         postgres    false    219            1           2606    19240    user user_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public."user" DROP CONSTRAINT user_pkey;
       public         postgres    false    207            ?           2606    19280 #   child_need child_need_Id_child_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.child_need
    ADD CONSTRAINT "child_need_Id_child_fkey" FOREIGN KEY (id_child) REFERENCES public.child(id);
 O   ALTER TABLE ONLY public.child_need DROP CONSTRAINT "child_need_Id_child_fkey";
       public       postgres    false    2861    205    213            @           2606    19285 "   child_need child_need_Id_need_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.child_need
    ADD CONSTRAINT "child_need_Id_need_fkey" FOREIGN KEY (id_need) REFERENCES public.need(id);
 N   ALTER TABLE ONLY public.child_need DROP CONSTRAINT "child_need_Id_need_fkey";
       public       postgres    false    2869    213    211            >           2606    19251    family family1_Id_child_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY public.family
    ADD CONSTRAINT "family1_Id_child_fkey" FOREIGN KEY (id_child) REFERENCES public.child(id);
 H   ALTER TABLE ONLY public.family DROP CONSTRAINT "family1_Id_child_fkey";
       public       postgres    false    2861    209    205            A           2606    19298 &   need_family need_family_Id_family_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.need_family
    ADD CONSTRAINT "need_family_Id_family_fkey" FOREIGN KEY (id_family) REFERENCES public.family(id);
 R   ALTER TABLE ONLY public.need_family DROP CONSTRAINT "need_family_Id_family_fkey";
       public       postgres    false    209    215    2867            B           2606    19303 $   need_family need_family_Id_need_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.need_family
    ADD CONSTRAINT "need_family_Id_need_fkey" FOREIGN KEY (id_need) REFERENCES public.need(id);
 P   ALTER TABLE ONLY public.need_family DROP CONSTRAINT "need_family_Id_need_fkey";
       public       postgres    false    215    211    2869            C           2606    19308 $   need_family need_family_Id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.need_family
    ADD CONSTRAINT "need_family_Id_user_fkey" FOREIGN KEY (id_user) REFERENCES public."user"(id);
 P   ALTER TABLE ONLY public.need_family DROP CONSTRAINT "need_family_Id_user_fkey";
       public       postgres    false    207    215    2865            D           2606    19321    payment payment_Id_need_fkey    FK CONSTRAINT     |   ALTER TABLE ONLY public.payment
    ADD CONSTRAINT "payment_Id_need_fkey" FOREIGN KEY (id_need) REFERENCES public.need(id);
 H   ALTER TABLE ONLY public.payment DROP CONSTRAINT "payment_Id_need_fkey";
       public       postgres    false    2869    217    211            E           2606    19326    payment payment_Id_user_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY public.payment
    ADD CONSTRAINT "payment_Id_user_fkey" FOREIGN KEY (id_user) REFERENCES public."user"(id);
 H   ALTER TABLE ONLY public.payment DROP CONSTRAINT "payment_Id_user_fkey";
       public       postgres    false    217    207    2865            F           2606    19339 &   user_family user_family_Id_family_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_family
    ADD CONSTRAINT "user_family_Id_family_fkey" FOREIGN KEY (id_family) REFERENCES public.family(id);
 R   ALTER TABLE ONLY public.user_family DROP CONSTRAINT "user_family_Id_family_fkey";
       public       postgres    false    209    219    2867            G           2606    19344 $   user_family user_family_Id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_family
    ADD CONSTRAINT "user_family_Id_user_fkey" FOREIGN KEY (id_user) REFERENCES public."user"(id);
 P   ALTER TABLE ONLY public.user_family DROP CONSTRAINT "user_family_Id_user_fkey";
       public       postgres    false    207    2865    219            �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �     
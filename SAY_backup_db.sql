PGDMP                          w           SAY_Test    11.4 (Debian 11.4-1.pgdg90+1)    11.4 �               0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                       false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                       false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                       false                       1262    18552    SAY_Test    DATABASE     z   CREATE DATABASE "SAY_Test" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';
    DROP DATABASE "SAY_Test";
             postgres    false            �            1259    18553    activity    TABLE     �   CREATE TABLE public.activity (
    "activityCode" integer NOT NULL,
    id integer NOT NULL,
    id_social_worker integer NOT NULL
);
    DROP TABLE public.activity;
       public         postgres    false            �            1259    18556    activity_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."activity_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public."activity_Id_seq";
       public       postgres    false    196                       0    0    activity_Id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public."activity_Id_seq" OWNED BY public.activity.id;
            public       postgres    false    197            �            1259    18558    activity_Id_social_worker_seq    SEQUENCE     �   CREATE SEQUENCE public."activity_Id_social_worker_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 6   DROP SEQUENCE public."activity_Id_social_worker_seq";
       public       postgres    false    196                       0    0    activity_Id_social_worker_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public."activity_Id_social_worker_seq" OWNED BY public.activity.id_social_worker;
            public       postgres    false    198            �            1259    18560    child    TABLE     �  CREATE TABLE public.child (
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
       public         postgres    false            �            1259    18572    child_ConfirmUser_seq    SEQUENCE     �   CREATE SEQUENCE public."child_ConfirmUser_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public."child_ConfirmUser_seq";
       public       postgres    false    199                       0    0    child_ConfirmUser_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public."child_ConfirmUser_seq" OWNED BY public.child."confirmUser";
            public       postgres    false    200            �            1259    18574    child_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."child_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public."child_Id_seq";
       public       postgres    false    199                       0    0    child_Id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public."child_Id_seq" OWNED BY public.child.id;
            public       postgres    false    201            �            1259    18576 
   child_need    TABLE     �   CREATE TABLE public.child_need (
    id_need integer NOT NULL,
    id integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_child integer NOT NULL
);
    DROP TABLE public.child_need;
       public         postgres    false            �            1259    18579    child_need_Id_child_seq    SEQUENCE     �   CREATE SEQUENCE public."child_need_Id_child_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public."child_need_Id_child_seq";
       public       postgres    false    202                       0    0    child_need_Id_child_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public."child_need_Id_child_seq" OWNED BY public.child_need.id_child;
            public       postgres    false    203            �            1259    18581    child_need_Id_need_seq    SEQUENCE     �   CREATE SEQUENCE public."child_need_Id_need_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public."child_need_Id_need_seq";
       public       postgres    false    202                       0    0    child_need_Id_need_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public."child_need_Id_need_seq" OWNED BY public.child_need.id_need;
            public       postgres    false    204            �            1259    18583    child_need_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."child_need_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public."child_need_Id_seq";
       public       postgres    false    202                       0    0    child_need_Id_seq    SEQUENCE OWNED BY     I   ALTER SEQUENCE public."child_need_Id_seq" OWNED BY public.child_need.id;
            public       postgres    false    205            �            1259    18585    family    TABLE     y   CREATE TABLE public.family (
    id integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_child integer NOT NULL
);
    DROP TABLE public.family;
       public         postgres    false            �            1259    18588    family_Id_child_seq    SEQUENCE     �   CREATE SEQUENCE public."family_Id_child_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public."family_Id_child_seq";
       public       postgres    false    206                        0    0    family_Id_child_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public."family_Id_child_seq" OWNED BY public.family.id_child;
            public       postgres    false    207            �            1259    18590    family_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."family_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public."family_Id_seq";
       public       postgres    false    206            !           0    0    family_Id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public."family_Id_seq" OWNED BY public.family.id;
            public       postgres    false    208            �            1259    18592    need    TABLE     �  CREATE TABLE public.need (
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
       public         postgres    false            �            1259    18603    need_ConfirmUser_seq    SEQUENCE     �   CREATE SEQUENCE public."need_ConfirmUser_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public."need_ConfirmUser_seq";
       public       postgres    false    209            "           0    0    need_ConfirmUser_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public."need_ConfirmUser_seq" OWNED BY public.need."confirmUser";
            public       postgres    false    210            �            1259    18605    need_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."need_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public."need_Id_seq";
       public       postgres    false    209            #           0    0    need_Id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public."need_Id_seq" OWNED BY public.need.id;
            public       postgres    false    211            �            1259    18607    need_family    TABLE     �   CREATE TABLE public.need_family (
    id integer NOT NULL,
    id_family integer NOT NULL,
    id_user integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_need integer NOT NULL
);
    DROP TABLE public.need_family;
       public         postgres    false            �            1259    18610    need_family_Id_family_seq    SEQUENCE     �   CREATE SEQUENCE public."need_family_Id_family_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public."need_family_Id_family_seq";
       public       postgres    false    212            $           0    0    need_family_Id_family_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public."need_family_Id_family_seq" OWNED BY public.need_family.id_family;
            public       postgres    false    213            �            1259    18612    need_family_Id_need_seq    SEQUENCE     �   CREATE SEQUENCE public."need_family_Id_need_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public."need_family_Id_need_seq";
       public       postgres    false    212            %           0    0    need_family_Id_need_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public."need_family_Id_need_seq" OWNED BY public.need_family.id_need;
            public       postgres    false    214            �            1259    18614    need_family_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."need_family_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public."need_family_Id_seq";
       public       postgres    false    212            &           0    0    need_family_Id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public."need_family_Id_seq" OWNED BY public.need_family.id;
            public       postgres    false    215            �            1259    18616    need_family_Id_user_seq    SEQUENCE     �   CREATE SEQUENCE public."need_family_Id_user_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public."need_family_Id_user_seq";
       public       postgres    false    212            '           0    0    need_family_Id_user_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public."need_family_Id_user_seq" OWNED BY public.need_family.id_user;
            public       postgres    false    216            �            1259    18618    ngo    TABLE     $  CREATE TABLE public.ngo (
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
       public         postgres    false            �            1259    18631 
   ngo_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."ngo_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public."ngo_Id_seq";
       public       postgres    false    217            (           0    0 
   ngo_Id_seq    SEQUENCE OWNED BY     ;   ALTER SEQUENCE public."ngo_Id_seq" OWNED BY public.ngo.id;
            public       postgres    false    218            �            1259    18633    payment    TABLE     �   CREATE TABLE public.payment (
    id integer NOT NULL,
    id_user integer NOT NULL,
    amount integer NOT NULL,
    "createdAt" date NOT NULL,
    id_need integer NOT NULL
);
    DROP TABLE public.payment;
       public         postgres    false            �            1259    18636    payment_Id_need_seq    SEQUENCE     �   CREATE SEQUENCE public."payment_Id_need_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public."payment_Id_need_seq";
       public       postgres    false    219            )           0    0    payment_Id_need_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public."payment_Id_need_seq" OWNED BY public.payment.id_need;
            public       postgres    false    220            �            1259    18638    payment_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."payment_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public."payment_Id_seq";
       public       postgres    false    219            *           0    0    payment_Id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public."payment_Id_seq" OWNED BY public.payment.id;
            public       postgres    false    221            �            1259    18640    payment_Id_user_seq    SEQUENCE     �   CREATE SEQUENCE public."payment_Id_user_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public."payment_Id_user_seq";
       public       postgres    false    219            +           0    0    payment_Id_user_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public."payment_Id_user_seq" OWNED BY public.payment.id_user;
            public       postgres    false    222            �            1259    18642    social_worker    TABLE     �  CREATE TABLE public.social_worker (
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
       public         postgres    false            �            1259    18654    social_worker_Id_ngo_seq    SEQUENCE     �   CREATE SEQUENCE public."social_worker_Id_ngo_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public."social_worker_Id_ngo_seq";
       public       postgres    false    223            ,           0    0    social_worker_Id_ngo_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public."social_worker_Id_ngo_seq" OWNED BY public.social_worker.id_ngo;
            public       postgres    false    224            �            1259    18656    social_worker_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."social_worker_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public."social_worker_Id_seq";
       public       postgres    false    223            -           0    0    social_worker_Id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public."social_worker_Id_seq" OWNED BY public.social_worker.id;
            public       postgres    false    225            �            1259    18658    social_worker_Id_type_seq    SEQUENCE     �   CREATE SEQUENCE public."social_worker_Id_type_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public."social_worker_Id_type_seq";
       public       postgres    false    223            .           0    0    social_worker_Id_type_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public."social_worker_Id_type_seq" OWNED BY public.social_worker.id_type;
            public       postgres    false    226            �            1259    18660    social_worker_type    TABLE     �   CREATE TABLE public.social_worker_type (
    id integer NOT NULL,
    name character varying NOT NULL,
    privilege integer NOT NULL
);
 &   DROP TABLE public.social_worker_type;
       public         postgres    false            �            1259    18666    social_worker_type_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."social_worker_type_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public."social_worker_type_Id_seq";
       public       postgres    false    227            /           0    0    social_worker_type_Id_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public."social_worker_type_Id_seq" OWNED BY public.social_worker_type.id;
            public       postgres    false    228            �            1259    18668    user    TABLE       CREATE TABLE public."user" (
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
    id integer NOT NULL
);
    DROP TABLE public."user";
       public         postgres    false            �            1259    18678    user_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."user_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public."user_Id_seq";
       public       postgres    false    229            0           0    0    user_Id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public."user_Id_seq" OWNED BY public."user".id;
            public       postgres    false    230            �            1259    18680    user_family    TABLE     �   CREATE TABLE public.user_family (
    id integer NOT NULL,
    id_family integer NOT NULL,
    "userRole" integer NOT NULL,
    "isDeleted" boolean NOT NULL,
    id_user integer NOT NULL
);
    DROP TABLE public.user_family;
       public         postgres    false            �            1259    18683    user_family_Id_family_seq    SEQUENCE     �   CREATE SEQUENCE public."user_family_Id_family_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public."user_family_Id_family_seq";
       public       postgres    false    231            1           0    0    user_family_Id_family_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public."user_family_Id_family_seq" OWNED BY public.user_family.id_family;
            public       postgres    false    232            �            1259    18685    user_family_Id_seq    SEQUENCE     �   CREATE SEQUENCE public."user_family_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public."user_family_Id_seq";
       public       postgres    false    231            2           0    0    user_family_Id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public."user_family_Id_seq" OWNED BY public.user_family.id;
            public       postgres    false    233            �            1259    18687    user_family_Id_user_seq    SEQUENCE     �   CREATE SEQUENCE public."user_family_Id_user_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public."user_family_Id_user_seq";
       public       postgres    false    231            3           0    0    user_family_Id_user_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public."user_family_Id_user_seq" OWNED BY public.user_family.id_user;
            public       postgres    false    234                       2604    18689    activity id    DEFAULT     l   ALTER TABLE ONLY public.activity ALTER COLUMN id SET DEFAULT nextval('public."activity_Id_seq"'::regclass);
 :   ALTER TABLE public.activity ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    197    196                       2604    18690    activity id_social_worker    DEFAULT     �   ALTER TABLE ONLY public.activity ALTER COLUMN id_social_worker SET DEFAULT nextval('public."activity_Id_social_worker_seq"'::regclass);
 H   ALTER TABLE public.activity ALTER COLUMN id_social_worker DROP DEFAULT;
       public       postgres    false    198    196            "           2604    18691    child id    DEFAULT     f   ALTER TABLE ONLY public.child ALTER COLUMN id SET DEFAULT nextval('public."child_Id_seq"'::regclass);
 7   ALTER TABLE public.child ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    201    199            #           2604    18692    child_need id_need    DEFAULT     z   ALTER TABLE ONLY public.child_need ALTER COLUMN id_need SET DEFAULT nextval('public."child_need_Id_need_seq"'::regclass);
 A   ALTER TABLE public.child_need ALTER COLUMN id_need DROP DEFAULT;
       public       postgres    false    204    202            $           2604    18693    child_need id    DEFAULT     p   ALTER TABLE ONLY public.child_need ALTER COLUMN id SET DEFAULT nextval('public."child_need_Id_seq"'::regclass);
 <   ALTER TABLE public.child_need ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    205    202            %           2604    18694    child_need id_child    DEFAULT     |   ALTER TABLE ONLY public.child_need ALTER COLUMN id_child SET DEFAULT nextval('public."child_need_Id_child_seq"'::regclass);
 B   ALTER TABLE public.child_need ALTER COLUMN id_child DROP DEFAULT;
       public       postgres    false    203    202            &           2604    18695 	   family id    DEFAULT     h   ALTER TABLE ONLY public.family ALTER COLUMN id SET DEFAULT nextval('public."family_Id_seq"'::regclass);
 8   ALTER TABLE public.family ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    208    206            '           2604    18696    family id_child    DEFAULT     t   ALTER TABLE ONLY public.family ALTER COLUMN id_child SET DEFAULT nextval('public."family_Id_child_seq"'::regclass);
 >   ALTER TABLE public.family ALTER COLUMN id_child DROP DEFAULT;
       public       postgres    false    207    206            -           2604    18697    need id    DEFAULT     d   ALTER TABLE ONLY public.need ALTER COLUMN id SET DEFAULT nextval('public."need_Id_seq"'::regclass);
 6   ALTER TABLE public.need ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    211    209            .           2604    18698    need_family id    DEFAULT     r   ALTER TABLE ONLY public.need_family ALTER COLUMN id SET DEFAULT nextval('public."need_family_Id_seq"'::regclass);
 =   ALTER TABLE public.need_family ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    215    212            /           2604    18699    need_family id_family    DEFAULT     �   ALTER TABLE ONLY public.need_family ALTER COLUMN id_family SET DEFAULT nextval('public."need_family_Id_family_seq"'::regclass);
 D   ALTER TABLE public.need_family ALTER COLUMN id_family DROP DEFAULT;
       public       postgres    false    213    212            0           2604    18700    need_family id_user    DEFAULT     |   ALTER TABLE ONLY public.need_family ALTER COLUMN id_user SET DEFAULT nextval('public."need_family_Id_user_seq"'::regclass);
 B   ALTER TABLE public.need_family ALTER COLUMN id_user DROP DEFAULT;
       public       postgres    false    216    212            1           2604    18701    need_family id_need    DEFAULT     |   ALTER TABLE ONLY public.need_family ALTER COLUMN id_need SET DEFAULT nextval('public."need_family_Id_need_seq"'::regclass);
 B   ALTER TABLE public.need_family ALTER COLUMN id_need DROP DEFAULT;
       public       postgres    false    214    212            9           2604    18702    ngo id    DEFAULT     b   ALTER TABLE ONLY public.ngo ALTER COLUMN id SET DEFAULT nextval('public."ngo_Id_seq"'::regclass);
 5   ALTER TABLE public.ngo ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    218    217            :           2604    18703 
   payment id    DEFAULT     j   ALTER TABLE ONLY public.payment ALTER COLUMN id SET DEFAULT nextval('public."payment_Id_seq"'::regclass);
 9   ALTER TABLE public.payment ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    221    219            ;           2604    18704    payment id_user    DEFAULT     t   ALTER TABLE ONLY public.payment ALTER COLUMN id_user SET DEFAULT nextval('public."payment_Id_user_seq"'::regclass);
 >   ALTER TABLE public.payment ALTER COLUMN id_user DROP DEFAULT;
       public       postgres    false    222    219            <           2604    18705    payment id_need    DEFAULT     t   ALTER TABLE ONLY public.payment ALTER COLUMN id_need SET DEFAULT nextval('public."payment_Id_need_seq"'::regclass);
 >   ALTER TABLE public.payment ALTER COLUMN id_need DROP DEFAULT;
       public       postgres    false    220    219            C           2604    18706    social_worker id    DEFAULT     v   ALTER TABLE ONLY public.social_worker ALTER COLUMN id SET DEFAULT nextval('public."social_worker_Id_seq"'::regclass);
 ?   ALTER TABLE public.social_worker ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    225    223            D           2604    18707    social_worker id_ngo    DEFAULT     ~   ALTER TABLE ONLY public.social_worker ALTER COLUMN id_ngo SET DEFAULT nextval('public."social_worker_Id_ngo_seq"'::regclass);
 C   ALTER TABLE public.social_worker ALTER COLUMN id_ngo DROP DEFAULT;
       public       postgres    false    224    223            E           2604    18708    social_worker id_type    DEFAULT     �   ALTER TABLE ONLY public.social_worker ALTER COLUMN id_type SET DEFAULT nextval('public."social_worker_Id_type_seq"'::regclass);
 D   ALTER TABLE public.social_worker ALTER COLUMN id_type DROP DEFAULT;
       public       postgres    false    226    223            F           2604    18709    social_worker_type id    DEFAULT     �   ALTER TABLE ONLY public.social_worker_type ALTER COLUMN id SET DEFAULT nextval('public."social_worker_type_Id_seq"'::regclass);
 D   ALTER TABLE public.social_worker_type ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    228    227            K           2604    18710    user id    DEFAULT     f   ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public."user_Id_seq"'::regclass);
 8   ALTER TABLE public."user" ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    230    229            L           2604    18711    user_family id    DEFAULT     r   ALTER TABLE ONLY public.user_family ALTER COLUMN id SET DEFAULT nextval('public."user_family_Id_seq"'::regclass);
 =   ALTER TABLE public.user_family ALTER COLUMN id DROP DEFAULT;
       public       postgres    false    233    231            M           2604    18712    user_family id_family    DEFAULT     �   ALTER TABLE ONLY public.user_family ALTER COLUMN id_family SET DEFAULT nextval('public."user_family_Id_family_seq"'::regclass);
 D   ALTER TABLE public.user_family ALTER COLUMN id_family DROP DEFAULT;
       public       postgres    false    232    231            N           2604    18713    user_family id_user    DEFAULT     |   ALTER TABLE ONLY public.user_family ALTER COLUMN id_user SET DEFAULT nextval('public."user_family_Id_user_seq"'::regclass);
 B   ALTER TABLE public.user_family ALTER COLUMN id_user DROP DEFAULT;
       public       postgres    false    234    231            �          0    18553    activity 
   TABLE DATA               H   COPY public.activity ("activityCode", id, id_social_worker) FROM stdin;
    public       postgres    false    196   ��       �          0    18560    child 
   TABLE DATA               �  COPY public.child ("phoneNumber", nationality, "avatarUrl", id, "housingStatus", "firstName", "lastName", "familyCount", education, "createdAt", "birthPlace", address, bio, "voiceUrl", id_ngo, id_social_worker, "confirmUser", "confirmDate", "sayName", "generatedCode", city, country, gender, "birthDate", status, "doneNeedCount", "spentCredit", "isDeleted", "isConfirmed", "bioSummary", "sayFamilyCount", "lastUpdate", "isMigrated", "migratedId", "migrateDate") FROM stdin;
    public       postgres    false    199   ��       �          0    18576 
   child_need 
   TABLE DATA               H   COPY public.child_need (id_need, id, "isDeleted", id_child) FROM stdin;
    public       postgres    false    202   �       �          0    18585    family 
   TABLE DATA               ;   COPY public.family (id, "isDeleted", id_child) FROM stdin;
    public       postgres    false    206   �       �          0    18592    need 
   TABLE DATA                 COPY public.need (id, name, "imageUrl", category, description, cost, "affiliateLinkUrl", "createdAt", receipts, progress, paid, "confirmDate", "confirmUser", "isDone", "isDeleted", "isConfirmed", type, "descriptionSummary", "lastUpdate", "isUrgent") FROM stdin;
    public       postgres    false    209   O�       �          0    18607    need_family 
   TABLE DATA               S   COPY public.need_family (id, id_family, id_user, "isDeleted", id_need) FROM stdin;
    public       postgres    false    212   ��                 0    18618    ngo 
   TABLE DATA               )  COPY public.ngo (id, "coordinatorId", name, "postalAddress", "emailAddress", "phoneNumber", "logoUrl", balance, "socialWorkerCount", "childrenCount", "registerDate", "lastUpdateDate", "isActive", "isDeleted", city, country, "currentSocialWorkerCount", "currentChildrenCount", website) FROM stdin;
    public       postgres    false    217   ��                 0    18633    payment 
   TABLE DATA               L   COPY public.payment (id, id_user, amount, "createdAt", id_need) FROM stdin;
    public       postgres    false    219   ��                 0    18642    social_worker 
   TABLE DATA               A  COPY public.social_worker (id, "generatedCode", id_ngo, id_type, "firstName", "lastName", "userName", password, "birthCertificateNumber", "idNumber", "idCardUrl", "passportNumber", "birthDate", "phoneNumber", "emergencyPhoneNumber", "emailAddress", "telegramId", "postalAddress", "avatarUrl", "childCount", "needCount", "bankAccountNumber", "bankAccountShebaNumber", "bankAccountCardNumber", "registerDate", "lastUpdateDate", "lastLoginDate", "lastLogoutDate", "passportUrl", "isActive", "isDeleted", gender, city, country, "currentChildCount", "currentNeedCount") FROM stdin;
    public       postgres    false    223   ��                 0    18660    social_worker_type 
   TABLE DATA               A   COPY public.social_worker_type (id, name, privilege) FROM stdin;
    public       postgres    false    227   ��                 0    18668    user 
   TABLE DATA                 COPY public."user" ("firstName", "lastName", credit, "avatarUrl", "phoneNumber", "userName", "createdAt", "lastUpdate", "birthDate", "birthPlace", "flagUrl", "emailAddress", gender, "isDeleted", city, country, "lastLogin", password, "spentCredit", "doneNeedCount", id) FROM stdin;
    public       postgres    false    229   �                 0    18680    user_family 
   TABLE DATA               V   COPY public.user_family (id, id_family, "userRole", "isDeleted", id_user) FROM stdin;
    public       postgres    false    231   4�       4           0    0    activity_Id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public."activity_Id_seq"', 1, false);
            public       postgres    false    197            5           0    0    activity_Id_social_worker_seq    SEQUENCE SET     N   SELECT pg_catalog.setval('public."activity_Id_social_worker_seq"', 1, false);
            public       postgres    false    198            6           0    0    child_ConfirmUser_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public."child_ConfirmUser_seq"', 1, false);
            public       postgres    false    200            7           0    0    child_Id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public."child_Id_seq"', 5, true);
            public       postgres    false    201            8           0    0    child_need_Id_child_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public."child_need_Id_child_seq"', 1, false);
            public       postgres    false    203            9           0    0    child_need_Id_need_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public."child_need_Id_need_seq"', 1, false);
            public       postgres    false    204            :           0    0    child_need_Id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public."child_need_Id_seq"', 68, true);
            public       postgres    false    205            ;           0    0    family_Id_child_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public."family_Id_child_seq"', 1, false);
            public       postgres    false    207            <           0    0    family_Id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public."family_Id_seq"', 5, true);
            public       postgres    false    208            =           0    0    need_ConfirmUser_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public."need_ConfirmUser_seq"', 1, false);
            public       postgres    false    210            >           0    0    need_Id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public."need_Id_seq"', 68, true);
            public       postgres    false    211            ?           0    0    need_family_Id_family_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public."need_family_Id_family_seq"', 1, false);
            public       postgres    false    213            @           0    0    need_family_Id_need_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public."need_family_Id_need_seq"', 1, false);
            public       postgres    false    214            A           0    0    need_family_Id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public."need_family_Id_seq"', 1, false);
            public       postgres    false    215            B           0    0    need_family_Id_user_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public."need_family_Id_user_seq"', 1, false);
            public       postgres    false    216            C           0    0 
   ngo_Id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public."ngo_Id_seq"', 1, true);
            public       postgres    false    218            D           0    0    payment_Id_need_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public."payment_Id_need_seq"', 1, false);
            public       postgres    false    220            E           0    0    payment_Id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public."payment_Id_seq"', 1, false);
            public       postgres    false    221            F           0    0    payment_Id_user_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public."payment_Id_user_seq"', 1, false);
            public       postgres    false    222            G           0    0    social_worker_Id_ngo_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public."social_worker_Id_ngo_seq"', 1, false);
            public       postgres    false    224            H           0    0    social_worker_Id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public."social_worker_Id_seq"', 4, true);
            public       postgres    false    225            I           0    0    social_worker_Id_type_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public."social_worker_Id_type_seq"', 1, false);
            public       postgres    false    226            J           0    0    social_worker_type_Id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public."social_worker_type_Id_seq"', 6, true);
            public       postgres    false    228            K           0    0    user_Id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public."user_Id_seq"', 1, false);
            public       postgres    false    230            L           0    0    user_family_Id_family_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public."user_family_Id_family_seq"', 1, false);
            public       postgres    false    232            M           0    0    user_family_Id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public."user_family_Id_seq"', 1, false);
            public       postgres    false    233            N           0    0    user_family_Id_user_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public."user_family_Id_user_seq"', 1, false);
            public       postgres    false    234            P           2606    18715    activity activity_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.activity DROP CONSTRAINT activity_pkey;
       public         postgres    false    196            T           2606    18717    child_need child_need_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.child_need
    ADD CONSTRAINT child_need_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.child_need DROP CONSTRAINT child_need_pkey;
       public         postgres    false    202            R           2606    18719    child child_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.child
    ADD CONSTRAINT child_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.child DROP CONSTRAINT child_pkey;
       public         postgres    false    199            V           2606    18721    family family_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.family
    ADD CONSTRAINT family_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.family DROP CONSTRAINT family_pkey;
       public         postgres    false    206            Z           2606    18723    need_family need_family_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.need_family
    ADD CONSTRAINT need_family_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.need_family DROP CONSTRAINT need_family_pkey;
       public         postgres    false    212            X           2606    18725    need need_pkey 
   CONSTRAINT     L   ALTER TABLE ONLY public.need
    ADD CONSTRAINT need_pkey PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.need DROP CONSTRAINT need_pkey;
       public         postgres    false    209            \           2606    18727    ngo ngo_pkey 
   CONSTRAINT     J   ALTER TABLE ONLY public.ngo
    ADD CONSTRAINT ngo_pkey PRIMARY KEY (id);
 6   ALTER TABLE ONLY public.ngo DROP CONSTRAINT ngo_pkey;
       public         postgres    false    217            ^           2606    18729    payment payment_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.payment DROP CONSTRAINT payment_pkey;
       public         postgres    false    219            `           2606    18731     social_worker social_worker_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public.social_worker
    ADD CONSTRAINT social_worker_pkey PRIMARY KEY (id);
 J   ALTER TABLE ONLY public.social_worker DROP CONSTRAINT social_worker_pkey;
       public         postgres    false    223            b           2606    18733 *   social_worker_type social_worker_type_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.social_worker_type
    ADD CONSTRAINT social_worker_type_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.social_worker_type DROP CONSTRAINT social_worker_type_pkey;
       public         postgres    false    227            d           2606    18735    user user_PhoneNumber_key 
   CONSTRAINT     a   ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "user_PhoneNumber_key" UNIQUE ("phoneNumber");
 G   ALTER TABLE ONLY public."user" DROP CONSTRAINT "user_PhoneNumber_key";
       public         postgres    false    229            h           2606    18737    user_family user_family_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.user_family
    ADD CONSTRAINT user_family_pkey PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.user_family DROP CONSTRAINT user_family_pkey;
       public         postgres    false    231            f           2606    18739    user user_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public."user" DROP CONSTRAINT user_pkey;
       public         postgres    false    229            i           2606    18740 #   child_need child_need_Id_child_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.child_need
    ADD CONSTRAINT "child_need_Id_child_fkey" FOREIGN KEY (id_child) REFERENCES public.child(id);
 O   ALTER TABLE ONLY public.child_need DROP CONSTRAINT "child_need_Id_child_fkey";
       public       postgres    false    202    199    2898            j           2606    18745 "   child_need child_need_Id_need_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.child_need
    ADD CONSTRAINT "child_need_Id_need_fkey" FOREIGN KEY (id_need) REFERENCES public.need(id);
 N   ALTER TABLE ONLY public.child_need DROP CONSTRAINT "child_need_Id_need_fkey";
       public       postgres    false    202    209    2904            k           2606    18750    family family1_Id_child_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY public.family
    ADD CONSTRAINT "family1_Id_child_fkey" FOREIGN KEY (id_child) REFERENCES public.child(id);
 H   ALTER TABLE ONLY public.family DROP CONSTRAINT "family1_Id_child_fkey";
       public       postgres    false    2898    199    206            l           2606    18755 &   need_family need_family_Id_family_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.need_family
    ADD CONSTRAINT "need_family_Id_family_fkey" FOREIGN KEY (id_family) REFERENCES public.family(id);
 R   ALTER TABLE ONLY public.need_family DROP CONSTRAINT "need_family_Id_family_fkey";
       public       postgres    false    206    212    2902            m           2606    18760 $   need_family need_family_Id_need_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.need_family
    ADD CONSTRAINT "need_family_Id_need_fkey" FOREIGN KEY (id_need) REFERENCES public.need(id);
 P   ALTER TABLE ONLY public.need_family DROP CONSTRAINT "need_family_Id_need_fkey";
       public       postgres    false    212    209    2904            n           2606    18765 $   need_family need_family_Id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.need_family
    ADD CONSTRAINT "need_family_Id_user_fkey" FOREIGN KEY (id_user) REFERENCES public."user"(id);
 P   ALTER TABLE ONLY public.need_family DROP CONSTRAINT "need_family_Id_user_fkey";
       public       postgres    false    212    2918    229            o           2606    18770    payment payment_Id_need_fkey    FK CONSTRAINT     |   ALTER TABLE ONLY public.payment
    ADD CONSTRAINT "payment_Id_need_fkey" FOREIGN KEY (id_need) REFERENCES public.need(id);
 H   ALTER TABLE ONLY public.payment DROP CONSTRAINT "payment_Id_need_fkey";
       public       postgres    false    209    2904    219            p           2606    18775    payment payment_Id_user_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY public.payment
    ADD CONSTRAINT "payment_Id_user_fkey" FOREIGN KEY (id_user) REFERENCES public."user"(id);
 H   ALTER TABLE ONLY public.payment DROP CONSTRAINT "payment_Id_user_fkey";
       public       postgres    false    229    219    2918            q           2606    18780 &   user_family user_family_Id_family_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_family
    ADD CONSTRAINT "user_family_Id_family_fkey" FOREIGN KEY (id_family) REFERENCES public.family(id);
 R   ALTER TABLE ONLY public.user_family DROP CONSTRAINT "user_family_Id_family_fkey";
       public       postgres    false    2902    206    231            r           2606    18785 $   user_family user_family_Id_user_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_family
    ADD CONSTRAINT "user_family_Id_user_fkey" FOREIGN KEY (id_user) REFERENCES public."user"(id);
 P   ALTER TABLE ONLY public.user_family DROP CONSTRAINT "user_family_Id_user_fkey";
       public       postgres    false    231    2918    229            �      x������ � �      �   c  x��X�N�V^����h�a��]�,Z�����R5
� %%(mw��,F}���xp�3��,��f�'��ι��6 ������~���G�G�8~oO�g�%��I��?<��1|���$/�7߼xGC[��÷�$��n�J�w�?;���;�I�����{;<�$�;��H|����ΫM<���o��"��w�vփ(����fZ�T�B�����4�q���N�q�ߣ;���*�1�MC5S����y��8�����LY�Baa��!��$�Be��3�7�O!��tOð>�&�:i����iDbYT_hf�ysU�yHsR��R��Ռ̠���6����U��PX��U�����~�0U�nB���54�2[�K�΢9��d�	=ӌ3�r�b�=��5g��q�|�ɺ:��X��K�/h�B�b&���d�B�)���!�+�� ^�&�.�s�W�b/=v�6���HӘ	�q��M[�j�	m���F�GV����ӂ�2N��y!ՕoE9���S�b^�)���6�q���L��փ�Ո�Nc�Y��nu��U�mb/������$�F���,)��UdK������#�y�f�Ŗ8���7�� ˓N��9�� ���6��No�m=�����']�m����ֻ3��p��8��022`K�ؕ��5x�Hl:@��g�еూ�� I�57m|��_?�eۍm�xنr��K8�����Ä p“��H[8�۔
l	H{=�MM+�Y#:/ᑈ�6>6<*�<�t���M�*�Xg��t�L�@����B]�a��`ð���EåM�hQ'6�n��Y5��r'ۚ2�I[��е���j,S��R�����Өb���C(:���o#p��]����邓�� ?!}�O��foA`5R�e�!�����>�@���!26Q�� 2f�����0Q]Q�Э�~����CIڈ�$�س&G�Q�&-��D���%s�$�н��)�do,�d�	�����ϼ��c�c,�2���ҹ����D*@��G� W���i�7r����gh)/�c)�(�15�Ձ�w���ۯI���g��TOBţ����rγ��$��̢���llJ5��K�e�I�-���� ������،�W���P�eH�1i�B��I�"uWꖼ"�&�}E��ZX�B׾0�4�*�ڇ\_7`��}��o`���i��4�zL-�4u[�||���u���Kn���İ!Y�̐�c20���	W�l��F8��"4ƪ	�_�0	�	�\�^ڎԁ��B��-/C	�)F�YH�Oog(0�2f��6�-C�G-R���J]rܜd� sj��A��>���`D*��3"wN':�LX.Tǣ�Q�"�tB���>�h�,[£�c,T�5�0����,M�(��l�$f�9�v[��#A�7(0G�s������ ��q�o(n�\}#����ٸ"P&��LT�)����G_,���0wp����8�xGdB�~'�V���������M���m�,� ��6}�+p�A!{����04��f�J�*��ׯT�5�M�Z����u[_��_ȇ8SN��]�^eN��,ͥ
��P]c9}���Iֈ���>����w5�ƃ ��8��)}�G��Y�O�W���8����O5��H�_�yG��@^_�=n�1#;��%ߤ�j]c��YCY�k���,B��gN% ���%����|�����y$�e���:�gK�Ԩv��F�[��F@jJw6���Ss��.ga���m&��m�ϩT�'I��������y#��Y�pI��J��Kֻ��Z>���;�o�Z��r��=��<����N7/9�0���ߓ���ڿ�I/p      �   �   x�%��m�0�s1��%����?Sl`�~�)a%��Æ�o�x��ۢ�6�v��n���yk��{2L7�1]��t��e+L����z[ؒ6����'���7�>�K���xJ��Ը����7������Ĕ�0�	���R)QR--B�؄q5r�j��j��_#G�}	)YR�--rI���!�SMjJF�����u_�Ք���Q�6��C������6�i��)锊.�~P--Z�޴�?c���f�      �   %   x�3�L�4�2�F\�@Ҙ�H�p�IS�=... `�1      �   (  x��]�r��>�O���`@2���\R[�C*U�r�"m�V&Y����"�L���59�4c�K�^�}�s �-O��i�dM�g(���� ��L��t���N܍�U4�&n�s�)�u~��J��s����?�k�u�]���ZG��ެUO��J�ڬ�T*�����׍f�Ҭ���ݠ�*����:\�7Njx�^�c� ?��������GǵF�Y?=l7_9'~_�o�Q4y��]7��]�/�h��p�K���r���At���.��=���xkԇ!=����_������}��M��׽u�	���Їg@�cz�e�@�d,�%��3=z���������^�\�@7�O~����x�5���:�l@u�s���.�Q��W,ye�T�舂W>(��G}S:�|'p^���:�M?��3ω>�x>��$����i��8�WxY�i�@z�%�P����������1�:ma�4��� �/�/����Oݏ�k� �@\�O�_h��v`X0����	~LL=��������%z�����D�k�F�����%\إVFH�Op���4.0����v�H�I�����M��^t�{���y��>O�tB!da	"���<pYV
'9��o�IM��)45;��������OY$� Ҝ�8���)(��0d�[���Fo�ĥvDN�C��0��}��"���=D�*��F��_ȟ�>B���3����8�7��&ڕ)�������.��4�{\h.p�=�W/�g������4�@22b��4Xkdu���raꮎ��7K��AK�֣�M����fo���܅�&O�h�c�5,���y͐J�J��E�5-O�w��!�������)\~
\�\&����K=�S#1{���%���Aw��g�^�Nmb)5�r��Q��y�z
��j�U��)��Rc�`�J���x�<H������.ѭ�<��3�N�i !�%��x5�¥&��ƒ,t�����0�/���S��)D��:LP��E�@�2!��N�H��>�K��]�hg��#�rpl��Y�Pe =�d�P5EE��ڙ�\5p��&O��܏]�>�Uy�Z�����Ej�d��%-e��Dq����Ad(9�Py6<�m�P� ������P��	�]�d��2y��}�Z*ҡ8�>Ջ�)�I��Uq7e��>@�A�
�3=q�쨁E7v��Rplj$Y����M����Ʃ�:��h�8��~�Ȯ�Jż�^�i���B�����r�<����ɎF@S����I�G�(ꤘL�������
F���x���$rq�%���F<�`+�
ù��?EZM��g8цd�=Kh���DDp�#\=h�F߅�L���GХ�$���7�����0<iQ�V9��<�E�c�ɗ��NX^���2�����U�%����V����鏝c�H�b��y)��li
_���Y��Z�TIE��+Fbk=5kT�i�=ADp"�F'�H[�]�յu�d�;~��w1�U�%I�:�^T�Ay��a��d�;JǍ��U���뱚I��v�Ŕ�P�<;�PG��c���۾���b��´^�QY�)S�V����	��j��|������}&�厗��(�����d4jR���H��5�����:�#�a�խ,,ҡ���T��r`ya��ڛ%ק�V�y�Z�dH����l�} ��"ȚD)їي�F�x�*���͚9������4�su?W���^Ѯ�o���������!��+Y��Dfu�+������-�qcX��ʹ �� '
�L��R�1���`G��S;����"-�i�c��=�(y���6s�<������*�8�{���c
�&�s��`���#-6��8�P�~V@�dI��;���K�n�m
7�޳"CLg-Lx�mW�®m@��U#vA�N�Ё|BZ��ܙ+~��{Z�uhú,�`th!-�І�X�rothZСñ'�\�~�-�����Q�%��@���^.�Hvrb#J�@��HEٺ@j��.Q��]H�B��˙�UY��6�ն��I�4�*�Né;0��?*�+9!�$B�՛������^��Z�BL��~|֑)�b ��.]~��u�p� kCc�C˳�b�E�������n��+@��ߎ����}�����n]�_�_ �/��<��~`�$g���EI��l�$G�I�%95��|��%��̟�Jr�Oh�zd���z�G�P="D�v�G�,���]��F��q�n���T�]�0���/[/t,Xk�-t����BǼ�N;���B�c�f����Y(t��T0��B��M��B�"�:�yp8�D^�رB�'��Bӷ[�0��9p�煎=+t,�
���z�� r�G_���a�б �\��A��viX��:�����Vh��a�ĚF�S��/0o��A��:�X���S�Xn�\��AP�l:4�m���:�@��������`?�=E�CZ�{4��dYJ��ޣ�:��m2(,y�_�6��)tH��dhY0�;�M�7�����6 ֌�ַ�l}ן��Mư.��6�-T���m2�ݒ���m2[�I�d�q~-��m2�`�H��&#���DZ��d��Ѣꑴ�M�`'2�&�W�6U=����DfeF��dv�zZ�&3O����p��<A�(��M� ���p���<M�(��W>�B�����зX�0�a(��jƊՌ0�U4�bY)��Ғpj`�U(�^8C�©a���<�p-	���Xb
�{#��%©a8V?�R.�>J8�>{��e�mQ      �      x������ � �           x�]�=N�@���)� 8Zې`*РH4#�U�#�k%�����=�#�($M�1k_��� �ћy��N�TfN[Z���'׆�f�F-hI�%hgf�R,��U[�JX��®������.��jV����Z4+3o*�ȯښ6�Ж�m-�A��(�?.�\�Yg�s�~7����Ó�>=)�������w�T^��ϓH�l�E�F
�TE�!�ջ��<-����L��0�b�=�H��L'�IJ��R�	H�|酮칁��N`>��G��8��M���            x������ � �         �  x��T�n1>;O�/��׻�@p�ꍋ%4ٟf!�F����*�My
��(Q[$ě���0ޥ�Iũ�q��ٱ��N(e�r�p����.�$p�vn�c7!��ﺓ����p�w��2N��9�8S2��E�KVP�� �P�%�'Z�Wόy��1ۯ��}�F��v�*�V>̠cF0��ƌ� �lP��{/Fe�eLQ�s��JK��U�Ǽ��2K��޷7��0�w����PR�8�	�<�	Ɛ��)"�wl/��7�����j����$pS����� �`�[���8Z���bHu(�?�m�.)p�$�����+Z}�<8����� ���,��5n~]WY�B�2)��*@G�J]H��r�Ge�b��&)k��Ūʔ�Z3��ʟ�W���O��C �5�X���a��w5����2��k��{e���P*�PI�"�e���	�2�bi�D0)6I�\#F�)�o��,�(�FMQYt���F���sn�� = =�/�!:�Q�Ģ��#��s��`/qc����9��
�{��喙�|߻
���3������Y��#t�͙;6��2��"���uk� k��;l��;{���z�=b`LQ�Jե��4�E�
�]��#E�����>[#����=lO1�F�Z�]�A=�ƽ6O����=�!��=�X!׏j>A�lu:��14�         ]   x�3�,.-H-RHL����4�2�,�O�L�Q(�/�N-�4�2�L��/J��K,�/�4�2��s�W �*�,
s�r;F"�p�qBL4����� �_�            x������ � �            x������ � �     
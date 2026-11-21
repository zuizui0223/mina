# 独立アミノ酸同位体データUSAP-DC 602094：公開記録は確認、新標本の取得はNO-GO

**2026-11-21 JST | Draft PR #214 only.** 新たな生態効果・栄養段階やポリニヤ回帰は一件も行っていない。

## 発見と研究上の優先順位

新しい一次原著 **Michelson et al. (2026), *Marine Ecology Progress Series*, DOI [10.3354/meps15233](https://doi.org/10.3354/meps15233)** に対応する、[USAP-DC dataset DOI 10.15784/602094](https://www.usap-dc.org/view/dataset/602094) は2026-09に公開。原ファイル `Michelson_2026_Adelie_Feathers_SIA_CSIA_Data.csv` は39.7kB、出版社掲載MD5 `f9a91c9d9bf3dba9607bf0767df8c206`。現代2000–2016と古標本1841–1995のアデリーペンギン羽毛でbulk δ15N、アミノ酸source（phenylalanine）とtrophic（glutamic acid）、**基線補正済みtrophic position** が収録される。

**この源こそ、旧冬100km沿岸ポリニヤ→夏糞光学δ15N負の関連に関して「餌の栄養段階差」なのか「海洋窒素同位体基線差」なのかを別測定で検討する候補**。ただし羽毛形成期/越冬採餌域と糞の夏食性は別時点・別組織であり、生の採集年を勝手に6–10月の先行冬に紐付けてはいけない。

この直接独立検証の条件は、[取得前に凍結した支持ゲート](FROZEN_USAP602094_ADELIE_AA_BASELINE_VS_TP_SOURCE_GATE.md)を参照。元の報告地域群集に独立site×真正feather-growth-yearが十分あってはじめて別コホートとして検討する。

## 実取得監査：公式APIは200でもCSVではなかった

- 出典 [USAP-DC公式v2 API](https://www.usap-dc.org/api/v2.0/doc) `GET /datafiles/{dataset_uid}/{file_name}` へ、公開元ファイルの正確な名前で要求。データセットmetadata `GET /datasets/602094` は **HTTP 200 application/json**。
- データ本体要求は **HTTP 200** だが、戻ったのは **14,556 bytes の `text/html`**。先頭は `<!DOCTYPE html PUBLIC ...` で、公開元のCSVではない。実取得body MD5 **`f2a101e0af378409857a84190b52a9e0`**、出版登録MD5 `f9a91c9d9bf3dba9607bf0767df8c206` と不一致。**成功したデータダウンロードではなく、HTMLページへ戻された事実**。公式サイトのダウンロード画面にはreCAPTCHA/確認手順が表示され、今回の自動取得でその手順を突破したとは主張しない。
- [実行 GitHub Actions #44847377168 SUCCESS（アクセス可否の判定ジョブ）](https://github.com/zuizui0223/mina/actions/runs/44847377168) の source gateは、意図どおり **`NO_GO_USAP_SOURCE_DOWNLOAD_UNVERIFIED`**。artifact **14682879213**、ZIP sha256 `d97ef0b472a5f2373d03ce50e87d4d676d13d4e74693b2defce1c371fb27809b`。真正データ0行、年site/組織ラベルやAA-TP値は未読。GitHub Actions SUCCESSは「安全にno-goを記録できた」意味であって実測データ入手成功ではない。

## 次に必要な入力・代替根拠

元CSVを使用する場合、USAP-DCの公開データ画面から正式に取得した原CSV（MD5 `f9a91c9d9bf3dba9607bf0767df8c206`）が必要。取得後の最初の工程も**採取年・真の羽毛形成年・位置・種・組織のmetaのみ**監査し、同年冬とつながるかを判定しなければならない。本人の確認が必要な公式アクセス制限を迂回して取得することはしない。別repoに値や同位体推定を捏造して補わない。

生態的解釈は、Michelson et al. (2023) [*Limnology & Oceanography*, DOI 10.1002/lno.12446](https://doi.org/10.1002/lno.12446) のAA同位体研究により、**長期的なbulk δ15N低下が基線同位体変化を反映し得る**ことが既知という保守的解釈にとどめる。2026年の新AA標本から当プロジェクトのポリニヤとの相関が出たとは言わない。

**現在地：新しい独立生物学的Yへのアクセスは未達。既存439 site×seasonの負関連と原著PLSR方法での頑健性は維持するが、実食性変化・窒素基線・餌供給との因果つながりは未確定。** main、既存凍結原稿は変更しない。

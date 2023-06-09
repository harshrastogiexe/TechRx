import { UserOutlined } from '@ant-design/icons';
import { Avatar } from 'antd';
import { type FC } from 'react';
import { type IUser } from '../../common/types';
import './UserProfileView.scss';

interface UserProfileViewProps {
	user: IUser;
}

const DEFAULT_HEADER_IMAGE =
	'https://images.unsplash.com/photo-1650455863499-5ad354d92b35?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2072&q=80';

const AVATAR_SIZE = 50;

export const UserProfileView: FC<UserProfileViewProps> = (props) => {
	const {
		payload: { id: user },
	} = props.user;
	const { name, email, headerImage, image } = user;

	return (
		<section className="user-profile-view">
			<header
				className="user-profile-view-header"
				style={{
					height: AVATAR_SIZE + 30,
					backgroundImage: `url(${headerImage ?? DEFAULT_HEADER_IMAGE})`,
					marginBottom: `calc(0.75rem + ${AVATAR_SIZE / 2}px)`,
				}}
			>
				<div className="avatar-wrapper">
					<Avatar src={image} icon={<UserOutlined />} size={AVATAR_SIZE} />
				</div>
			</header>
			<section className="user-profile-view-body user" title={name}>
				<h4 className="name">{name}</h4>
				<span className="email">{email}</span>
			</section>
		</section>
	);
};
